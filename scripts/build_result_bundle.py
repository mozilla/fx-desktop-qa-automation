"""Build a backend-neutral result bundle from a STARfox pytest run.

See TESTING_AS_A_SERVICE.md. Reads the pytest-json-report output(s) produced by
the CI configs in ``config/`` and emits, into ``--out``:

    summary.json   the versioned result contract (schemas/result-summary-v1.json)
    junit.xml      headless + headed JUnit merged into a single document

Why both formats: JUnit is what every CI system already parses, but it cannot
express which Firefox build was under test, nor which failures were flakes. A
test that fails twice and passes on the third attempt is recorded by
pytest-json-report as outcome ``rerun``; JUnit records it as a plain pass. The
verdict therefore has to come from the JSON report, not the XML.

The execution backend (GitHub Actions today, possibly Taskcluster later) is
referenced only through optional env fallbacks, so the same bundle can be
produced from any runner.
"""

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET

SCHEMA_VERSION = "1.0"

# pytest-json-report outcomes -> our buckets. "rerun" means the test failed at
# least once and then passed within --reruns, i.e. a flake. A test that
# exhausts its retries and still fails is reported as "failed".
OUTCOME_BUCKETS = {
    "passed": "passed",
    "failed": "failed",
    "error": "error",
    "skipped": "skipped",
    "xfailed": "xfailed",
    "xpassed": "xpassed",
    "rerun": "flaky",
}
FAILING_BUCKETS = ("failed", "error")
# worse outcome wins when merging, so a merge can never hide a failure
SEVERITY = {"error": 3, "failed": 3, "flaky": 2}
REPORT_FILES = ("report.json", "report_headed.json")
JUNIT_FILES = ("junit.xml", "junit_headed.xml")
BUCKET_KEYS = ("passed", "failed", "error", "skipped", "xfailed", "xpassed", "flaky")


def suite_of(nodeid: str) -> str:
    """tests/downloads/test_x.py::test_y -> 'downloads'."""
    path = nodeid.replace("\\", "/").split("::")[0]
    parts = [p for p in path.split("/") if p]
    if len(parts) >= 2 and parts[0] == "tests":
        return parts[1]
    return parts[-2] if len(parts) >= 2 else "unknown"


def failure_message(test: dict) -> str:
    """Pull the most specific failure text available for a test."""
    for phase in ("call", "setup", "teardown"):
        stage = test.get(phase) or {}
        crash = stage.get("crash") or {}
        if crash.get("message"):
            return str(crash["message"]).strip()
        if stage.get("longrepr"):
            return str(stage["longrepr"]).strip().splitlines()[-1]
    return "no failure detail recorded"


def test_duration(test: dict) -> float:
    phases = ("setup", "call", "teardown")
    return round(sum((test.get(p) or {}).get("duration", 0.0) for p in phases), 3)


def load_reports(artifacts_dir: str) -> tuple[list[dict], list[str]]:
    """Return (merged tests, infra errors) from every json report we can find.

    The headless run uses ``-m 'not headed'`` and the headed run uses
    ``-m 'headed'``, so the two sets are disjoint by construction. Collisions
    are still handled defensively via SEVERITY.
    """
    merged: dict[str, dict] = {}
    infra: list[str] = []
    found_any = False

    for name in REPORT_FILES:
        path = os.path.join(artifacts_dir, name)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                report = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            infra.append(f"{name} could not be read: {exc}")
            continue

        found_any = True

        # A collector that blew up means tests never ran: our fault, not the build's.
        for collector in report.get("collectors") or []:
            if collector.get("outcome") == "failed":
                infra.append(f"collection failed for {collector.get('nodeid', '?')}")

        tests = report.get("tests") or []
        if not tests and not (report.get("summary") or {}).get("collected"):
            infra.append(f"{name} collected zero tests")

        for test in tests:
            nodeid = test.get("nodeid", "")
            prev = merged.get(nodeid)
            if prev is None:
                merged[nodeid] = test
                continue
            bucket = OUTCOME_BUCKETS.get(test.get("outcome", ""), "failed")
            prev_bucket = OUTCOME_BUCKETS.get(prev.get("outcome", ""), "failed")
            if SEVERITY.get(bucket, 1) > SEVERITY.get(prev_bucket, 1):
                merged[nodeid] = test

    if not found_any:
        infra.append(
            f"no pytest json report found in {artifacts_dir!r} "
            f"(looked for {', '.join(REPORT_FILES)}) - the test run did not complete"
        )

    return list(merged.values()), infra


def build_metadata(tests: list[dict], args) -> dict:
    """Build info, preferring per-test metadata and falling back to env.

    conftest.py sets fx_version / machine_config inside the driver fixture, so
    a run where Firefox never launched has no metadata at all. Hence fallbacks.
    """
    fx_version = machine_config = None
    for test in tests:
        meta = test.get("metadata") or {}
        fx_version = fx_version or meta.get("fx_version")
        machine_config = machine_config or meta.get("machine_config")
        if fx_version and machine_config:
            break

    version = args.build_version or fx_version or os.environ.get("FX_VERSION")
    return {
        "channel": args.channel or os.environ.get("FX_CHANNEL") or "unknown",
        "version": version or "unknown",
        "platform": args.platform,
        "machine_config": machine_config or "unknown",
        "source_url": args.source_url or os.environ.get("FX_DOWNLOAD_URL") or "",
    }


def compute_verdict(totals: dict, infra_errors: list[str]) -> str:
    if infra_errors:
        return "infra_error"
    if totals["failed"] or totals["error"]:
        return "fail"
    if totals["flaky"]:
        return "flaky"
    return "pass"


def gate_failed(verdict: str, fail_on: str) -> bool:
    if fail_on == "never":
        return False
    if fail_on == "any-failure":
        return verdict != "pass"
    # non-flaky-failure (default): a flake alone must not fail a caller's gate
    return verdict in ("fail", "infra_error")


def build_summary(tests: list[dict], infra_errors: list[str], args) -> dict:
    totals = dict.fromkeys(BUCKET_KEYS, 0)
    failures = []

    for test in tests:
        bucket = OUTCOME_BUCKETS.get(test.get("outcome", ""), "failed")
        totals[bucket] = totals.get(bucket, 0) + 1
        if bucket in FAILING_BUCKETS or bucket == "flaky":
            failures.append(
                {
                    "nodeid": test.get("nodeid", ""),
                    "suite": suite_of(test.get("nodeid", "")),
                    "outcome": bucket,
                    "flaky": bucket == "flaky",
                    # a flake's final attempt passed, so it carries no crash detail
                    "message": (
                        "passed on retry"
                        if bucket == "flaky"
                        else failure_message(test)
                    ),
                    "duration_s": test_duration(test),
                }
            )

    # real failures first, flakes after
    failures.sort(key=lambda f: (f["flaky"], f["nodeid"]))
    verdict = compute_verdict(totals, infra_errors)

    return {
        "schema_version": SCHEMA_VERSION,
        "request_id": args.request_id or os.environ.get("STARFOX_REQUEST_ID") or "",
        "verdict": verdict,
        "gate": {"fail_on": args.fail_on, "failed": gate_failed(verdict, args.fail_on)},
        "run": {
            "url": args.run_url or os.environ.get("STARFOX_RUN_URL") or "",
            "backend": args.backend,
        },
        "build": build_metadata(tests, args),
        "selection": {
            "test_set": args.test_set or os.environ.get("STARFOX_SPLIT") or "",
            "test_count": len(tests),
            "suites": sorted({suite_of(t.get("nodeid", "")) for t in tests}),
        },
        "totals": totals,
        "failures": failures,
        "infra_errors": infra_errors,
    }


def merge_junit(artifacts_dir: str, out_path: str) -> bool:
    """Combine the headless and headed JUnit documents into one."""
    root = ET.Element("testsuites")
    agg = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    total_time = 0.0
    found = False

    for name in JUNIT_FILES:
        path = os.path.join(artifacts_dir, name)
        if not os.path.isfile(path):
            continue
        try:
            parsed = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        found = True
        label = "headed" if "headed" in name else "headless"
        # pytest emits <testsuites><testsuite>...; tolerate a bare <testsuite>
        suites = [parsed] if parsed.tag == "testsuite" else list(parsed)
        for suite in suites:
            suite.set("name", f"{suite.get('name', 'pytest')}.{label}")
            for key in agg:
                agg[key] += int(suite.get(key) or 0)
            total_time += float(suite.get("time") or 0)
            root.append(suite)

    if not found:
        return False

    for key, value in agg.items():
        root.set(key, str(value))
    root.set("time", f"{total_time:.3f}")
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    ET.ElementTree(root).write(out_path, encoding="utf-8", xml_declaration=True)
    return True


def step_summary(summary: dict) -> str:
    t = summary["totals"]
    icon = {
        "pass": "[PASS]",
        "flaky": "[FLAKY]",
        "fail": "[FAIL]",
        "infra_error": "[INFRA]",
    }
    build = summary["build"]
    lines = [
        f"### {icon.get(summary['verdict'], '')} Firefox {build['platform']} "
        f"- {summary['verdict'].upper()}",
        "",
        f"**Build:** `{build['version']}` ({build['channel']}) on {build['machine_config']}",
        f"**Test set:** `{summary['selection']['test_set'] or 'n/a'}` "
        f"({summary['selection']['test_count']} tests)",
        "",
        "| passed | failed | error | flaky | skipped | xfailed |",
        "|---|---|---|---|---|---|",
        f"| {t['passed']} | {t['failed']} | {t['error']} | {t['flaky']} "
        f"| {t['skipped']} | {t['xfailed']} |",
    ]
    if summary["infra_errors"]:
        lines += ["", "**Infrastructure errors (not a build regression):**", ""]
        lines += [f"- {e}" for e in summary["infra_errors"]]
    real = [f for f in summary["failures"] if not f["flaky"]]
    if real:
        lines += ["", f"**Failures ({len(real)}):**", ""]
        lines += [f"- `{f['nodeid']}` - {f['message'][:160]}" for f in real[:25]]
        if len(real) > 25:
            lines.append(f"- ...and {len(real) - 25} more")
    flakes = [f for f in summary["failures"] if f["flaky"]]
    if flakes:
        lines += ["", f"**Flakes ({len(flakes)}, passed on retry):**", ""]
        lines += [f"- `{f['nodeid']}`" for f in flakes[:15]]
    return "\n".join(lines) + "\n"


def emit(path_env: str, content: str) -> None:
    path = os.environ.get(path_env)
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(content)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build a STARfox result bundle.")
    ap.add_argument(
        "--artifacts-dir", required=True, help="dir with report*.json / junit*.xml"
    )
    ap.add_argument("--out", required=True, help="output dir for the bundle")
    ap.add_argument("--platform", required=True, choices=["windows", "macos", "linux"])
    ap.add_argument(
        "--fail-on",
        default="non-flaky-failure",
        choices=["any-failure", "non-flaky-failure", "never"],
    )
    ap.add_argument("--channel", default="")
    ap.add_argument("--build-version", default="")
    ap.add_argument("--source-url", default="")
    ap.add_argument("--test-set", default="")
    ap.add_argument("--request-id", default="")
    ap.add_argument("--run-url", default="")
    ap.add_argument("--backend", default="github-actions")
    ap.add_argument(
        "--infra-error",
        action="append",
        default=[],
        dest="infra_error",
        help="record a workflow-detected infrastructure failure (repeatable)",
    )
    ap.add_argument(
        "--enforce",
        action="store_true",
        help="exit non-zero when the fail_on policy is violated",
    )
    args = ap.parse_args(argv)

    tests, infra_errors = load_reports(args.artifacts_dir)
    infra_errors = list(args.infra_error) + infra_errors
    summary = build_summary(tests, infra_errors, args)

    os.makedirs(args.out, exist_ok=True)
    summary_path = os.path.join(args.out, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
        fh.write("\n")

    if not merge_junit(args.artifacts_dir, os.path.join(args.out, "junit.xml")):
        print(f"warning: no JUnit XML found in {args.artifacts_dir}", file=sys.stderr)

    print(json.dumps(summary["totals"]))
    print(f"verdict={summary['verdict']} gate_failed={summary['gate']['failed']}")
    print(f"wrote {summary_path}")

    emit("GITHUB_STEP_SUMMARY", step_summary(summary))
    emit(
        "GITHUB_OUTPUT",
        f"verdict={summary['verdict']}\ngate_failed={str(summary['gate']['failed']).lower()}\n",
    )

    return 1 if (args.enforce and summary["gate"]["failed"]) else 0


if __name__ == "__main__":
    sys.exit(main())
