import logging
from dotenv import load_dotenv
from modules.testrail_integration import testrail_init

# Load environment variables from .env file
load_dotenv()

# Configuration Constants
PROJECT_ID = 17  # The ID of the TestRail project to work with
SUITE_NAMES = ["PDF Viewer"]  # List of suite names to process

CUSTOM_SUB_TEST_SUITES = [2]  # Value to set for the 'custom_sub_test_suites' field
updated_count = 0
DRY_RUN = True  # If True, only log actions without making changes


def get_all_cases_from_suite(tr, project_id, suite_id):
    """
    Fetch all test cases from a given TestRail suite using pagination.

    Args:
        tr: TestRail API client instance.
        project_id (int): The ID of the TestRail project.
        suite_id (int): The ID of the suite to fetch cases from.

    Returns:
        list: A list of test case dictionaries.
    """
    all_cases = []  # List to store all fetched test cases
    offset = 0  # Starting point for pagination
    limit = 240  # Maximum number of cases to fetch in each API call

    while True:
        # Build the API endpoint with pagination parameters
        endpoint = f"get_cases/{project_id}&suite_id={suite_id}&limit={limit}&offset={offset}"
        response = tr.client.send_get(endpoint)  # Send API request to TestRail
        cases = response.get("cases", [])  # Extract the list of test cases

        if not cases:
            # If no more cases are found, break the loop
            break

        # Add the fetched cases to the complete list
        all_cases.extend(cases)

        if len(cases) < limit:
            # If the number of fetched cases is less than the limit, we are at the last page
            break

        # Increment offset to fetch the next batch of cases
        offset += limit

    # Log the total number of fetched cases
    logging.info(f"Total cases fetched from suite {suite_id}: {len(all_cases)}")
    return all_cases


if __name__ == "__main__":
    # Initialize logging to display info messages
    logging.basicConfig(level=logging.INFO)

    # Initialize the TestRail API client
    tr = testrail_init()

    # Fetch suite IDs matching the given suite names
    suites = tr.get_suites(PROJECT_ID)
    suite_ids = [suite["id"] for suite in suites if suite["name"] in SUITE_NAMES]
    logging.info(f"Found suites: {suite_ids}")

    # Fetch all test cases from the selected suites
    all_cases = []  # List to store all fetched test cases
    for suite_id in suite_ids:
        # Fetch and add cases from each suite
        cases = get_all_cases_from_suite(tr, PROJECT_ID, suite_id)
        all_cases.extend(cases)

    # Log the total number of test cases found
    logging.info(f"Total test cases found for selected suites: {len(all_cases)}")

    updated_count = 0  # Counter for the number of cases updated

    # Iterate through all cases
    for case in all_cases:
        case_id = case["id"]

        type_id = case.get("type_id")
        current_custom_value = case.get("custom_sub_test_suites", "Not Set")

        logging.info(f"Case ID {case_id} type_id: {type_id}")

        if type_id != 6:
            logging.info(f"Skipping case {case_id} – type_id = {type_id}")
            continue

        logging.info(
            f"Case ID {case_id} matches (type_id == 6). "
            f"Current custom_sub_test_suites: {current_custom_value}"
        )

        if not DRY_RUN:
            result = tr.update_case_field(case_id, "custom_sub_test_suites", [2])
            logging.info(f"Updated case {case_id} to '[2]', Result: {result}")
        else:
            logging.info(f"[DRY RUN] Would update case {case_id} from '{current_custom_value}' to '[2]'.")

        updated_count += 1
