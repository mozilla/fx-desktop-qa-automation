"""Maintain the Smart Window (S70279) smoke suite and automation fields in TestRail.

Three idempotent edits, driven by the groups in
``~/Documents/starfox/s70279_smoke_suite_and_jira_plan.md``:

* every case in the smoke suite gains the "Smoke & Sanity" sub test suite,
  keeping whatever it already carries;
* cases with a test in ``tests/smart_window/`` are set to automation status
  Completed, with coverage judged per case (Full only where the test asserts
  every expected result in the TestRail case);
* smoke cases that are not automated yet are set to Suitable, so a filter on
  "Smoke & Sanity" reads as a progress view rather than a flat list.

Option ids are resolved from ``get_case_fields``; the mapping in
``testrail_status_analyses.py`` is wrong on both the labels and the option
count. ``custom_sub_test_suites`` is multi-select and TestRail replaces rather
than appends, so the existing value is read back and merged.

Dry run by default. Pass ``--apply`` to write.
"""

import argparse
import logging
import os
import sys

from modules.testrail import APIError
from modules.testrail_integration import testrail_init

PROJECT_ID = 17
SUITE_ID = 70279

# Smoke suite, grouped as the Jira children of epic DTE-5295.
SMOKE_GROUPS = {
    "Window lifecycle and switching": [
        3248785,
        3248786,
        3309849,
        3309851,
        3309853,
        3309854,
        3309852,
        4062295,
    ],
    "Smart Bar input and search": [3248361, 3248362, 3321908, 3321894, 3977124],
    "AI chat": [3311329, 3374375, 3978359, 3322038, 3374374],
    "AI tab actions": [4120777, 4220532],
    "History and chat history": [3313457, 3313455],
    "Settings and AI controls": [3310319, 3310316, 3310318],
    "Onboarding and sign-in": [3240165, 3371305, 3392590, 3371299, 3392591],
    "Session restore": [3309859, 3309861],
}
SMOKE_CASES = [c for group in SMOKE_GROUPS.values() for c in group]

# Coverage is judged per case: Full only where the test asserts every expected
# result in the TestRail case, Partial where a named expected result is out of
# reach. Reasoning per case is in s70279_smoke_selection.md.
FULL_COVERAGE = [3248361, 3309851, 3309853, 3309854, 3321887, 3321908, 3978359]
PARTIAL_COVERAGE = [
    3240165,
    3248362,
    3248785,
    3248786,
    3309849,
    3309859,
    3310319,
    3311329,
    3313457,
    3349915,
    3371305,
    3374375,
    3392590,
]
AUTOMATED_CASES = FULL_COVERAGE + PARTIAL_COVERAGE

# Smoke cases with no test yet: automatable with today's harness, so Suitable.
SUITABLE_CASES = [c for c in SMOKE_CASES if c not in AUTOMATED_CASES]

SMOKE_LABEL = "Smoke & Sanity"
COMPLETED_LABEL, SUITABLE_LABEL = "Completed", "Suitable"
FULL_LABEL, PARTIAL_LABEL, NONE_LABEL = "Full", "Partial", "None"


def load_credentials():
    """Read testrail_credentials.env into the environment, if present."""
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    path = os.path.join(root, "testrail_credentials.env")
    if not os.path.exists(path):
        return
    with open(path) as handle:
        for line in handle:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def option_ids(tr, system_name):
    """Map a dropdown/multiselect field's option labels to their ids."""
    for field in tr.get_custom_fields():
        if field["system_name"] != system_name:
            continue
        for config in field["configs"]:
            items = config["options"].get("items")
            if items:
                return {
                    label.strip(): int(value.strip())
                    for value, label in (
                        line.split(",", 1) for line in items.splitlines() if "," in line
                    )
                }
    raise SystemExit(f"No options found for {system_name}; check the field config.")


def fetch_cases(tr, project_id, suite_id):
    """Fetch every case in a suite, following pagination."""
    cases, offset, limit = {}, 0, 240
    while True:
        response = tr.client.send_get(
            f"get_cases/{project_id}&suite_id={suite_id}&limit={limit}&offset={offset}"
        )
        batch = response.get("cases", [])
        if not batch:
            break
        cases.update({case["id"]: case for case in batch})
        if len(batch) < limit:
            break
        offset += limit
    return cases


def plan_changes(cases, smoke_id, ids):
    """Return {case_id: {field: value}} for cases that are not already correct."""
    changes = {}
    for case_id in sorted(set(SMOKE_CASES) | set(AUTOMATED_CASES)):
        case = cases.get(case_id)
        if case is None:
            logging.warning("C%s is not in suite S%s -- skipping.", case_id, SUITE_ID)
            continue

        fields = {}
        if case_id in AUTOMATED_CASES:
            status = ids[COMPLETED_LABEL]
            coverage = (
                ids[FULL_LABEL] if case_id in FULL_COVERAGE else ids[PARTIAL_LABEL]
            )
        else:
            # Suitable keeps coverage None, the invariant the coverage-reset
            # script enforces across the project.
            status, coverage = ids[SUITABLE_LABEL], ids[NONE_LABEL]

        if case.get("custom_automation_status") != status:
            fields["custom_automation_status"] = status
        if case.get("custom_automation_coverage") != coverage:
            fields["custom_automation_coverage"] = coverage

        if case_id in SMOKE_CASES:
            current = case.get("custom_sub_test_suites") or []
            if smoke_id not in current:
                fields["custom_sub_test_suites"] = sorted(set(current) | {smoke_id})

        if fields:
            changes[case_id] = fields
    return changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="Write. Omit for a dry run."
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    load_credentials()

    tr = testrail_init()
    if tr is None:
        raise SystemExit(
            "TestRail session could not be initialized; check credentials."
        )

    # testrail_init() only builds the client, so bad credentials surface here.
    try:
        sub_suites = option_ids(tr, "custom_sub_test_suites")
        ids = option_ids(tr, "custom_automation_status")
        ids.update(option_ids(tr, "custom_automation_coverage"))
        cases = fetch_cases(tr, PROJECT_ID, SUITE_ID)
    except APIError as error:
        if "401" in str(error):
            raise SystemExit(
                "TestRail rejected the credentials. Generate a fresh key at "
                "TestRail > My Settings > API Keys and put it in testrail_credentials.env."
            ) from error
        if "403" in str(error):
            raise SystemExit(
                "TestRail refused the write. Project 17's default role is Read-only, so "
                "the account needs a project role or a group that carries one."
            ) from error
        raise

    logging.info(
        "Smoke suite: %s cases (%s automated, %s to automate).",
        len(SMOKE_CASES),
        len([c for c in SMOKE_CASES if c in AUTOMATED_CASES]),
        len(SUITABLE_CASES),
    )
    changes = plan_changes(cases, sub_suites[SMOKE_LABEL], ids)
    if not changes:
        logging.info("Nothing to do -- every case already has the target values.")
        return

    for case_id, fields in sorted(changes.items()):
        logging.info("C%s %s", case_id, cases[case_id]["title"][:58])
        for field, value in sorted(fields.items()):
            logging.info("    %s: %r -> %r", field, cases[case_id].get(field), value)

    if not args.apply:
        logging.info(
            "Dry run: %s cases would change. Re-run with --apply.", len(changes)
        )
        return

    for case_id, fields in sorted(changes.items()):
        tr.update_test_case(case_id, **fields)
    logging.info("Applied changes to %s cases.", len(changes))


if __name__ == "__main__":
    sys.exit(main())
