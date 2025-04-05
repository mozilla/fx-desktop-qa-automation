import os
import logging
from modules.testrail_integration import testrail_init

# Configuration
PROJECT_ID = 17
SUITE_NAMES = ["Bookmarks and History", "Drag and Drop", "Find Toolbar"]
AUTOMATION_COVERAGE_VALUE = 3
COMPLETED_STATUS_ID = 4

# Set TestRail credentials
os.environ["TESTRAIL_BASE_URL"] = "https://mozilla.testrail.io"
os.environ["TESTRAIL_USERNAME"] = ""
os.environ["TESTRAIL_API_KEY"] = ""


def get_all_completed_cases(tr, project_id, suite_id):
    """Fetch all completed automated test cases (custom_automation_status = 4)"""
    response = tr._get_test_cases(project_id, suite_id)
    cases = response.get("cases", [])

    # Filter cases that are automated & completed (custom_automation_status == 4)
    completed_cases = [case for case in cases if case.get("custom_automated_test_names") and case.get("custom_automation_status") == 4]
    logging.info(f"Total cases fetched from suite {suite_id}: {len(completed_cases)}")
    return completed_cases


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tr = testrail_init()

    # Get suite IDs for the selected suite names
    suites = tr.get_suites(PROJECT_ID)
    suite_ids = [suite["id"] for suite in suites if suite["name"] in SUITE_NAMES]
    logging.info(f"Found suites: {suite_ids}")

    all_completed_cases = []
    for suite_id in suite_ids:
        completed_cases = get_all_completed_cases(tr, PROJECT_ID, suite_id)
        all_completed_cases.extend(completed_cases)

    logging.info(f"Total completed automated cases found for selected suites: {len(all_completed_cases)}")

    for case in all_completed_cases:
        tr.update_case_field(case["id"], "custom_automation_coverage", AUTOMATION_COVERAGE_VALUE)

    logging.info("All applicable test cases updated successfully!")
