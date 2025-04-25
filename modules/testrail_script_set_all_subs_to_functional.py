import os
import logging
from modules.testrail_integration import testrail_init

# Configuration
PROJECT_ID = 17
# SUITE_NAMES = ["Bookmarks and History", "Drag and Drop", "Find Toolbar", "Audio/Video", "Downloads", "WebRTC"]
CUSTOM_SUB_TEST_SUITES = 1  # "Functional Only"

# Set TestRail credentials
os.environ["TESTRAIL_BASE_URL"] = "https://mozilla.testrail.io"
os.environ["TESTRAIL_USERNAME"] = ""
os.environ["TESTRAIL_API_KEY"] = ""


def get_all_cases_from_suite(tr, project_id, suite_id):
    """Fetch all test cases in the suite"""
    response = tr._get_test_cases(project_id, suite_id)
    cases = response.get("cases", [])
    logging.info(f"Total cases fetched from suite {suite_id}: {len(cases)}")
    return cases


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tr = testrail_init()

    # Get suite IDs for the selected suite names
    suites = tr.get_suites(PROJECT_ID)
    suite_ids = [suite["id"] for suite in suites]
    logging.info(f"Found suites: {suite_ids}")

    all_cases = []
    for suite_id in suite_ids:
        cases = get_all_cases_from_suite(tr, PROJECT_ID, suite_id)
        all_cases.extend(cases)

    logging.info(f"Total test cases found for selected suites: {len(all_cases)}")

    for case in all_cases:
        tr.update_case_field(case["id"], "custom_sub_tests_suites", CUSTOM_SUB_TEST_SUITES)

    logging.info("All applicable test cases updated to 'Functional Only' successfully!")
