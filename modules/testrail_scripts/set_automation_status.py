"""Mark TestRail cases Completed, with their automation coverage, once a test covers them.

A case is only changed if a test under tests/ returns its id from test_case and
that test is marked pass in manifests/key.yaml. Dry run by default.

    uv run python -m modules.testrail_scripts.set_automation_status \\
        --full C4120777 --partial C4220532 C3392591 [--apply]

Needs TESTRAIL_BASE_URL, TESTRAIL_USERNAME and TESTRAIL_API_KEY.
"""

import argparse
import logging
import re
import sys
from pathlib import Path

import yaml

from modules.testrail import APIError
from modules.testrail_integration import testrail_init

ROOT = Path(__file__).resolve().parents[2]
TESTS = ROOT / "tests"
MANIFEST = ROOT / "manifests" / "key.yaml"

# The test_case fixture's body: an optional docstring, then `return "<digits>"`.
CASE_ID_RE = re.compile(
    r'def test_case\(\):\s*(?:"""[\s\S]*?"""\s*)?return\s+"(\d+)"', re.MULTILINE
)

COMPLETED = "Completed"
COVERAGE_LABELS = {"full": "Full", "partial": "Partial"}


def case_id(text: str) -> int:
    """Parse "C4120777" or "4120777" into 4120777."""
    match = re.fullmatch(r"[Cc]?(\d+)", text.strip())
    if not match:
        raise argparse.ArgumentTypeError(f"not a TestRail case id: {text!r}")
    return int(match.group(1))


def find_tests(case_ids: set[int]) -> dict[int, list[Path]]:
    """Map each case id to the test files whose test_case fixture returns it."""
    found = {case: [] for case in case_ids}
    for path in sorted(TESTS.rglob("test_*.py")):
        match = CASE_ID_RE.search(path.read_text())
        if match and int(match.group(1)) in found:
            found[int(match.group(1))].append(path)
    return found


def manifest_results(path: Path, manifest: dict) -> list[str]:
    """Return every result key.yaml gives a test file: per platform and per subtest."""
    entry = manifest.get(path.parent.name, {}).get(path.stem)
    if not entry:
        return []
    entries = [entry] if "result" in entry else list(entry.values())
    results = []
    for item in entries:
        result = item.get("result")
        results.extend(result.values() if isinstance(result, dict) else [result])
    return results


def option_ids(tr, system_name: str) -> dict[str, int]:
    """Map a dropdown field's option labels to their ids, as TestRail defines them."""
    for field in tr.get_custom_fields():
        if field["system_name"] != system_name:
            continue
        for config in field["configs"]:
            items = config["options"].get("items")
            if items:
                return {
                    label.strip(): int(value)
                    for value, label in (
                        line.split(",", 1) for line in items.splitlines() if "," in line
                    )
                }
    raise SystemExit(f"TestRail has no options for {system_name}.")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    coverage_help = {
        "full": "Cases whose test checks every expected result in the case",
        "partial": "Cases whose test checks only some expected results",
    }
    for name, help_text in coverage_help.items():
        parser.add_argument(
            f"--{name}",
            nargs="+",
            type=case_id,
            default=[],
            metavar="CASE",
            help=help_text,
        )
    parser.add_argument(
        "--apply", action="store_true", help="Write. Omit for a dry run."
    )
    args = parser.parse_args(argv)
    both = set(args.full) & set(args.partial)
    if both:
        parser.error(f"given as both full and partial: {sorted(both)}")
    if not args.full and not args.partial:
        parser.error("give at least one case with --full or --partial")
    return args


def main(argv=None):
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    coverage_for = {case: "full" for case in args.full}
    coverage_for.update({case: "partial" for case in args.partial})

    manifest = yaml.safe_load(MANIFEST.read_text())
    tests = find_tests(set(coverage_for))
    refused = []
    for case, paths in sorted(tests.items()):
        results = [r for path in paths for r in manifest_results(path, manifest)]
        if "pass" not in results:
            where = ", ".join(str(p.relative_to(ROOT)) for p in paths) or "no test file"
            refused.append(f"C{case}: {where}, results {results or 'none'}")
    if refused:
        raise SystemExit(
            "Not automated here, so not marking Completed:\n  " + "\n  ".join(refused)
        )

    tr = testrail_init()
    if tr is None:
        raise SystemExit(
            "Set TESTRAIL_BASE_URL, TESTRAIL_USERNAME and TESTRAIL_API_KEY."
        )

    try:
        status_ids = option_ids(tr, "custom_automation_status")
        coverage_ids = option_ids(tr, "custom_automation_coverage")
        names = {
            "custom_automation_status": {v: k for k, v in status_ids.items()},
            "custom_automation_coverage": {v: k for k, v in coverage_ids.items()},
        }
        changes = {}
        for case in sorted(coverage_for):
            current = tr.client.send_get(f"get_case/{case}")
            target = {
                "custom_automation_status": status_ids[COMPLETED],
                "custom_automation_coverage": coverage_ids[
                    COVERAGE_LABELS[coverage_for[case]]
                ],
            }
            fields = {k: v for k, v in target.items() if current.get(k) != v}
            label = f"C{case} {current['title'][:60]}"
            if not fields:
                logging.info(
                    "%s: already %s, %s.", label, COMPLETED, coverage_for[case]
                )
                continue
            changes[case] = fields
            logging.info(label)
            for field, value in fields.items():
                before = names[field].get(current.get(field), current.get(field))
                logging.info("    %s: %s -> %s", field, before, names[field][value])

        if not changes:
            logging.info("Nothing to change.")
            return
        if not args.apply:
            logging.info(
                "Dry run: %s cases would change. Re-run with --apply.", len(changes)
            )
            return
        for case, fields in changes.items():
            tr.update_test_case(case, **fields)
        logging.info("Updated %s cases.", len(changes))
    except APIError as error:
        if "HTTP 401" in str(error):
            raise SystemExit(
                "TestRail rejected the credentials. Check TESTRAIL_USERNAME, and that "
                "the API key was saved under My Settings > API Keys."
            ) from error
        if "HTTP 403" in str(error):
            raise SystemExit(
                "TestRail refused the write: the account needs edit rights on project 17."
            ) from error
        raise


if __name__ == "__main__":
    sys.exit(main())
