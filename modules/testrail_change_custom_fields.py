# This script, as it is right now, can be run safely. It won't make any changes to the Uninstaller
# suite because there is nothing to change; no tests with Automation Status: Complete (4).
# I've added back a couple of Debug statements that print logging info. Those helped me understand what
# TestRail is returning.

import json  # Import json to pretty-print API responses (test case infortmation
import logging
import os
import sys

# Import from TestRail wasn't working, So I had to force it this way.
# Get the absolute path of the project's root directory
project_root = os.path.abspath(os.path.dirname(__file__))

# Add 'modules/' to sys.path
sys.path.insert(0, os.path.join(project_root, "modules"))

# Now import TestRail
from testrail import APIError as err
from testrail import TestRail

# Configuration - Update these values accordingly
TESTRAIL_HOST = "https://mozilla.testrail.io"
USERNAME = "twalker@mozilla.com"  # "your_username"
PASSWORD = "6GG8ucf1/.YAHWXRZ1o1-SNhMu9jCqhu5xxS.P7uT"  # "your_api_key"
TESTRAIL_FX_DESK_PRJ_ID = 17
# SUITE_IDS = [
#     43517,
#     65,
#     5403,
# ]  # Test suite ID's for Password Manager, PDF Viewer, Preferences

# Uninstaller suite and non-existent suite used for safe(ish) debugging.
SUITE_IDS = [2052, 0]

# Field names and values
AUTOMATION_STATUS = "custom_automation_status"
AUTOMATION_COVERAGE = "custom_automation_coverage"
FULL_COVERAGE_VALUE = int(3)

# Initialize TestRail API client
testrail_api = TestRail(TESTRAIL_HOST, USERNAME, PASSWORD)


def get_cases_to_update(project_id, suite_id):
    """Fetch test cases from a suite and return only those where automation status is 2 (Completed)."""
    logging.info(f"Fetching test cases from suite {suite_id}...")

    try:
        response = testrail_api.client.send_get(
            f"get_cases/{project_id}&suite_id={suite_id}"
        )
        test_cases = response.get("cases", [])

        if not test_cases:
            logging.warning(f"No test cases found in suite {suite_id}.")
            return []

        # Debug: Print first test case information to inspect in logging output
        if test_cases:
            logging.info(f"First test case: {json.dumps(test_cases[0], indent=2)}")

        # Debug: Print the first few test cases and their automation status
        logging.info(
            f"Checking automation statuses for test cases in suite {suite_id}..."
        )
        for case in test_cases[:5]:  # Print first 5 cases in the test suite
            logging.info(
                f"Case ID {case['id']} - Automation Status: {case.get('custom_automation_status')}"
            )

        # Filter cases where automation status is 4 (Completed)
        cases_to_update = [
            case
            for case in test_cases
            if isinstance(case, dict) and case.get("custom_automation_status") == 4
        ]

        logging.info(
            f"Found {len(cases_to_update)} test cases with automation status 'Completed' (4) in suite {suite_id}."
        )
        return cases_to_update

    except err as e:
        logging.error(f"TestRail API error: {e}")
        return []


def update_test_case_field(case_id):
    """Update a test case's automation coverage to Full (3) using update_case_field."""
    try:
        testrail_api.update_case_field(
            case_id, AUTOMATION_COVERAGE, FULL_COVERAGE_VALUE
        )
        logging.info(
            f"Updated case {case_id}: Set {AUTOMATION_COVERAGE} to {FULL_COVERAGE_VALUE}."
        )
    except Exception as e:
        logging.error(f"Failed to update case {case_id}: {e}")


def process_suites(suite_ids):
    """Iterate over multiple test suites and update applicable test cases."""
    for suite_id in suite_ids:
        logging.info(f"Processing suite {suite_id}...")
        cases_to_update = get_cases_to_update(TESTRAIL_FX_DESK_PRJ_ID, suite_id)

        if not cases_to_update:
            logging.info(f"No cases to update in suite {suite_id}. Skipping...")
            continue

        # Update the automation completed test cases
        for case in cases_to_update:
            update_test_case_field(case["id"])

        logging.info(f"Finished processing suite {suite_id}.\n")


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    process_suites(SUITE_IDS)
    logging.info("All applicable test cases have been updated (pending approval).")


if __name__ == "__main__":
    main()
