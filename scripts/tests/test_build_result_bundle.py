"""Unit tests for scripts/build_result_bundle.py (see TESTING_AS_A_SERVICE.md)."""

import json
import subprocess
import sys
import textwrap
import xml.etree.ElementTree as ET

import pytest

from scripts.build_result_bundle import (
    build_summary,
    compute_verdict,
    gate_failed,
    load_reports,
    main,
    merge_junit,
    suite_of,
)

SCHEMA_PATH = "schemas/result-summary-v1.json"


class Args:
    """Stand-in for the argparse namespace."""

    def __init__(self, **kw):
        defaults = dict(
            platform="linux",
            fail_on="non-flaky-failure",
            channel="beta",
            build_version="155.0b2",
            source_url="",
            test_set="smoke",
            request_id="req-1",
            run_url="",
            backend="github-actions",
        )
        defaults.update(kw)
        self.__dict__.update(defaults)


def write_report(path, tests, collected=None, collectors=None):
    path.write_text(
        json.dumps(
            {
                "summary": {
                    "collected": len(tests) if collected is None else collected
                },
                "collectors": collectors or [],
                "tests": tests,
            }
        ),
        encoding="utf-8",
    )


def t(nodeid, outcome, message=None):
    test = {"nodeid": nodeid, "outcome": outcome, "call": {"duration": 1.0}}
    if message:
        test["call"]["crash"] = {"message": message}
    return test


# --------------------------------------------------------------------------
# The assumption the whole script rests on: how a flake is represented.
# --------------------------------------------------------------------------


def test_pytest_json_report_marks_a_retried_pass_as_rerun(tmp_path):
    """Pin the plugin behaviour that flake classification depends on.

    A test that fails then passes within --reruns must appear as outcome
    'rerun', not 'passed'. If pytest-json-report ever changes this, the
    verdict logic silently starts calling flakes clean passes - so assert it
    against the real plugin rather than a hand-written fixture.
    """
    (tmp_path / "test_f.py").write_text(
        textwrap.dedent("""
            import os
            C = os.path.join(os.path.dirname(os.path.abspath(__file__)), "n")
            def test_flaky():
                n = int(open(C).read()) if os.path.exists(C) else 0
                open(C, "w").write(str(n + 1))
                assert n >= 2
            def test_hard_fail():
                assert False
        """),
        encoding="utf-8",
    )
    out = tmp_path / "r.json"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(tmp_path / "test_f.py"),
            "-p",
            "no:cacheprovider",
            "--json-report",
            "--json-report-file",
            str(out),
            "--reruns",
            "3",
            "-q",
            "--no-header",
        ],
        cwd=tmp_path,
        capture_output=True,
        check=False,
    )
    outcomes = {
        x["nodeid"].split("::")[-1]: x["outcome"]
        for x in json.loads(out.read_text(encoding="utf-8"))["tests"]
    }
    assert outcomes["test_flaky"] == "rerun", outcomes
    assert outcomes["test_hard_fail"] == "failed", outcomes


def test_flaky_is_not_counted_as_passed(tmp_path):
    write_report(
        tmp_path / "report.json",
        [
            t("tests/tabs/test_a.py::test_a", "passed"),
            t("tests/tabs/test_b.py::test_b", "rerun"),
        ],
    )
    tests, infra = load_reports(str(tmp_path))
    s = build_summary(tests, infra, Args())
    assert s["totals"] == {
        "passed": 1,
        "failed": 0,
        "error": 0,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0,
        "flaky": 1,
    }
    assert s["verdict"] == "flaky"
    assert [f["flaky"] for f in s["failures"]] == [True]


# --------------------------------------------------------------------------
# Verdict / gate policy
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "totals_kw,infra,expected",
    [
        ({}, [], "pass"),
        ({"flaky": 1}, [], "flaky"),
        ({"failed": 1}, [], "fail"),
        ({"error": 1}, [], "fail"),
        ({"failed": 1, "flaky": 2}, [], "fail"),
        ({}, ["download failed"], "infra_error"),
        ({"failed": 3}, ["download failed"], "infra_error"),
    ],
)
def test_verdict(totals_kw, infra, expected):
    totals = dict.fromkeys(
        ["passed", "failed", "error", "skipped", "xfailed", "xpassed", "flaky"], 0
    )
    totals.update(totals_kw)
    assert compute_verdict(totals, infra) == expected


@pytest.mark.parametrize(
    "verdict,fail_on,expected",
    [
        ("pass", "any-failure", False),
        ("flaky", "any-failure", True),
        ("flaky", "non-flaky-failure", False),
        ("fail", "non-flaky-failure", True),
        ("infra_error", "non-flaky-failure", True),
        ("fail", "never", False),
        ("infra_error", "never", False),
    ],
)
def test_gate(verdict, fail_on, expected):
    assert gate_failed(verdict, fail_on) is expected


# --------------------------------------------------------------------------
# Infrastructure-error detection (distinguishing "we broke" from "build broke")
# --------------------------------------------------------------------------


def test_missing_report_is_infra_error(tmp_path):
    tests, infra = load_reports(str(tmp_path))
    assert tests == []
    assert any("did not complete" in e for e in infra)
    assert build_summary(tests, infra, Args())["verdict"] == "infra_error"


def test_zero_collected_is_infra_error(tmp_path):
    write_report(tmp_path / "report.json", [], collected=0)
    _, infra = load_reports(str(tmp_path))
    assert any("zero tests" in e for e in infra)


def test_failed_collector_is_infra_error(tmp_path):
    write_report(
        tmp_path / "report.json",
        [t("tests/tabs/test_a.py::test_a", "passed")],
        collectors=[{"nodeid": "tests/broken.py", "outcome": "failed"}],
    )
    _, infra = load_reports(str(tmp_path))
    assert any("collection failed" in e for e in infra)


def test_unreadable_report_is_infra_error(tmp_path):
    (tmp_path / "report.json").write_text("{not json", encoding="utf-8")
    _, infra = load_reports(str(tmp_path))
    assert any("could not be read" in e for e in infra)


# --------------------------------------------------------------------------
# Merging the headless and headed runs
# --------------------------------------------------------------------------


def test_merges_headless_and_headed(tmp_path):
    write_report(
        tmp_path / "report.json", [t("tests/tabs/test_a.py::test_a", "passed")]
    )
    write_report(
        tmp_path / "report_headed.json", [t("tests/menus/test_b.py::test_b", "passed")]
    )
    tests, infra = load_reports(str(tmp_path))
    assert infra == []
    s = build_summary(tests, infra, Args())
    assert s["totals"]["passed"] == 2
    assert s["selection"]["suites"] == ["menus", "tabs"]


def test_merge_conflict_takes_the_worse_outcome(tmp_path):
    """A merge must never be able to hide a failure."""
    write_report(
        tmp_path / "report.json", [t("tests/tabs/test_a.py::test_a", "passed")]
    )
    write_report(
        tmp_path / "report_headed.json", [t("tests/tabs/test_a.py::test_a", "failed")]
    )
    tests, _ = load_reports(str(tmp_path))
    assert len(tests) == 1
    assert build_summary(tests, [], Args())["totals"]["failed"] == 1


def test_merge_junit_combines_documents(tmp_path):
    for name, case, failures in (
        ("junit.xml", "test_a", 0),
        ("junit_headed.xml", "test_b", 1),
    ):
        body = "<failure message='x'/>" if failures else ""
        (tmp_path / name).write_text(
            f"<testsuites><testsuite name='pytest' tests='1' failures='{failures}' "
            f"errors='0' skipped='0' time='1.0'>"
            f"<testcase classname='c' name='{case}'>{body}</testcase></testsuite></testsuites>",
            encoding="utf-8",
        )
    out = tmp_path / "merged.xml"
    assert merge_junit(str(tmp_path), str(out))
    root = ET.parse(out).getroot()
    assert root.get("tests") == "2"
    assert root.get("failures") == "1"
    assert sorted(s.get("name") for s in root) == ["pytest.headed", "pytest.headless"]


def test_merge_junit_returns_false_when_absent(tmp_path):
    assert merge_junit(str(tmp_path), str(tmp_path / "out.xml")) is False


# --------------------------------------------------------------------------
# Misc + schema conformance
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "nodeid,expected",
    [
        ("tests/downloads/test_x.py::test_y", "downloads"),
        (r"tests\downloads\test_x.py::test_y", "downloads"),
        ("l10n_CM/foo/test_x.py::test_y", "foo"),
        ("test_x.py::test_y", "unknown"),
    ],
)
def test_suite_of(nodeid, expected):
    assert suite_of(nodeid) == expected


def test_build_metadata_prefers_test_metadata_over_env(tmp_path, monkeypatch):
    monkeypatch.setenv("FX_VERSION", "from-env")
    test = t("tests/tabs/test_a.py::test_a", "passed")
    test["metadata"] = {
        "fx_version": "155.0b9-build2",
        "machine_config": "Linux 24 x86_64",
    }
    write_report(tmp_path / "report.json", [test])
    tests, _ = load_reports(str(tmp_path))
    build = build_summary(tests, [], Args(build_version=""))["build"]
    assert build["version"] == "155.0b9-build2"
    assert build["machine_config"] == "Linux 24 x86_64"


def test_build_metadata_falls_back_to_env_when_firefox_never_launched(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("FX_VERSION", "155.0b9-build2")
    write_report(
        tmp_path / "report.json", [t("tests/tabs/test_a.py::test_a", "failed")]
    )
    tests, _ = load_reports(str(tmp_path))
    assert (
        build_summary(tests, [], Args(build_version=""))["build"]["version"]
        == "155.0b9-build2"
    )


def check_schema(instance, schema, path="$"):
    """Minimal JSON Schema check for the subset used by our schemas.

    Deliberately not jsonschema: adding a runtime dependency to this repo means
    every contributor reruns `uv sync`, which is too high a price for one test.
    """
    if "const" in schema:
        assert instance == schema["const"], f"{path}: expected const {schema['const']}"
    if "enum" in schema:
        assert instance in schema["enum"], (
            f"{path}: {instance!r} not in {schema['enum']}"
        )
    types = {
        "object": dict,
        "array": list,
        "string": str,
        "boolean": bool,
        "integer": int,
        "number": (int, float),
    }
    if (ty := schema.get("type")) in types:
        if ty == "integer":
            assert isinstance(instance, int) and not isinstance(instance, bool), (
                f"{path}: int"
            )
        else:
            assert isinstance(instance, types[ty]), (
                f"{path}: expected {ty}, got {type(instance)}"
            )
    if schema.get("type") == "object":
        for key in schema.get("required", []):
            assert key in instance, f"{path}: missing required {key!r}"
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = set(instance) - set(props)
            assert not extra, f"{path}: unexpected keys {extra}"
        for key, value in instance.items():
            if key in props:
                check_schema(value, props[key], f"{path}.{key}")
    if schema.get("type") == "array" and "items" in schema:
        for i, item in enumerate(instance):
            check_schema(item, schema["items"], f"{path}[{i}]")
    if "minimum" in schema:
        assert instance >= schema["minimum"], f"{path}: below minimum"


def test_summary_conforms_to_published_schema(tmp_path):
    write_report(
        tmp_path / "report.json",
        [
            t("tests/tabs/test_a.py::test_a", "passed"),
            t("tests/tabs/test_b.py::test_b", "failed", "TimeoutException: nope"),
            t("tests/menus/test_c.py::test_c", "rerun"),
            t("tests/menus/test_d.py::test_d", "skipped"),
        ],
    )
    tests, infra = load_reports(str(tmp_path))
    summary = build_summary(tests, infra, Args())
    with open(SCHEMA_PATH, encoding="utf-8") as fh:
        check_schema(summary, json.load(fh))


def test_main_writes_bundle_and_enforces_gate(tmp_path, monkeypatch):
    art, out = tmp_path / "artifacts", tmp_path / "out"
    art.mkdir()
    write_report(
        art / "report.json", [t("tests/tabs/test_a.py::test_a", "failed", "boom")]
    )
    (art / "junit.xml").write_text(
        "<testsuites><testsuite name='pytest' tests='1' failures='1' errors='0' "
        "skipped='0' time='1.0'><testcase classname='c' name='test_a'>"
        "<failure message='boom'/></testcase></testsuite></testsuites>",
        encoding="utf-8",
    )
    summary_file = tmp_path / "step_summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_file))

    argv = ["--artifacts-dir", str(art), "--out", str(out), "--platform", "linux"]
    assert main(argv) == 0, "without --enforce the script must not fail the job"
    assert main([*argv, "--enforce"]) == 1
    assert main([*argv, "--enforce", "--fail-on", "never"]) == 0

    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert summary["verdict"] == "fail"
    assert summary["failures"][0]["message"] == "boom"
    assert (out / "junit.xml").exists()
    assert "[FAIL]" in summary_file.read_text(encoding="utf-8")
