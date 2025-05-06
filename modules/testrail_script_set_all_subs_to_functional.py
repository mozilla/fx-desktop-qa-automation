import os
import logging
from modules.testrail_integration import testrail_init

# Configuration
PROJECT_ID = 17
SUITE_NAMES = ["Downloads"]
CUSTOM_SUB_TEST_SUITES = 1  # "Functional Only"

# Set TestRail credentials
os.environ["TESTRAIL_BASE_URL"] = "https://mozilla.testrail.io"
os.environ["TESTRAIL_USERNAME"] = "hyacoub@mozilla.com"
os.environ["TESTRAIL_API_KEY"] = "HrENZ5FSSxiI1xl3DTMF-NMm1qGug2bVZM3NCALhV"


def get_all_cases_from_suite(tr, project_id, suite_id):
    """Fetch all test cases from a suite by handling pagination."""
    all_cases = []
    offset = 0
    limit = 240  # Default limit for TestRail API is 250

    while True:
        # Build endpoint with pagination parameters
        endpoint = (
            f"get_cases/{project_id}&suite_id={suite_id}&limit={limit}&offset={offset}"
        )
        response = tr.client.send_get(endpoint)
        cases = response.get("cases", [])
        if not cases:
            break
        all_cases.extend(cases)
        # If the number of cases returned is less than the limit, we've reached the last page.
        if len(cases) < limit:
            break
        offset += limit

    logging.info(f"Total cases fetched from suite {suite_id}: {len(all_cases)}")
    return all_cases


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tr = testrail_init()

    # Get suite IDs for the selected suite names
    suites = tr.get_suites(PROJECT_ID)
    # suite_ids = [suite["id"] for suite in suites]
    suite_ids = [suite["id"] for suite in suites if suite["name"] in SUITE_NAMES]
    logging.info(f"Found suites: {suite_ids}")

    all_cases = []
    for suite_id in suite_ids:
        cases = get_all_cases_from_suite(tr, PROJECT_ID, suite_id)
        all_cases.extend(cases)

    logging.info(f"Total test cases found for selected suites: {len(all_cases)}")

    for case in all_cases:
        result = tr.update_case_field(case["id"], "custom_sub_tests_suites", CUSTOM_SUB_TEST_SUITES)
        logging.debug(f"Updated case {case['id']} result: {result}")

    logging.info("All applicable test cases updated to 'Functional Only' successfully!")

    # Re-verify that all cases have been updated correctly
    logging.info("Verifying that all test cases were updated correctly...")
    failed_updates = []

    for suite_id in suite_ids:
        updated_cases = get_all_cases_from_suite(tr, PROJECT_ID, suite_id)
        for case in updated_cases:
            if case.get("custom_sub_tests_suites") != CUSTOM_SUB_TEST_SUITES:
                failed_updates.append(case["id"])

    if failed_updates:
        logging.warning(f"The following case IDs were not updated correctly: {failed_updates}")
        logging.warning(f"Number of failed updates: {len(failed_updates)}")

    else:
        logging.info("All test cases have the correct 'custom_sub_tests_suites' value.")
