import logging
from dotenv import load_dotenv
from modules.testrail_integration import testrail_init

# Load environment variables from .env file (like API credentials)
load_dotenv()

# Configuration Constants
PROJECT_ID = 17  # ID of the TestRail project to work with
SUITE_NAMES = [
    "Address Bar 138+",
    "Address Bar and Search <136 (to use with late beta) - locked",
    "Address Bar and Search Scotch Bonnet (to use with early beta)",
    "Audio/Video",
    "Bookmarks and History",
    "Build Branding",
    "Downloads",
    "Drag and Drop",
    "Find Toolbar",
    "Form Autofill",
    "Geolocation",
    "Language Packs",
    "Menus",
    "Networking",
    "Notifications, Push Notifications and Alerts",
    "PDF Viewer",
    "Password manager",
    "Preferences",
    "Printing",
    "Reader View",
    "Scrolling, Panning and Zooming",
    "Security and Privacy",
    "Startup and Profile",
    "Sync & Firefox Account",
    "Tabbed Browser",
    "Theme and Toolbar Customization"
]  # Only process suites with this name

CUSTOM_SUB_TEST_SUITES = [2]  # Value to set for 'custom_sub_test_suites' field (e.g. 'Smoke')
DRY_RUN = True  # If True, simulate updates without sending changes


def get_all_cases_from_suite(tr, project_id, suite_id):
    """
    Fetch all test cases from a given TestRail suite using pagination.

    Args:
        tr: TestRail API client instance.
        project_id (int): The TestRail project ID.
        suite_id (int): The specific suite ID within the project.

    Returns:
        list: All test cases as a list of dictionaries.
    """
    all_cases = []  # List to hold all fetched cases
    offset = 0      # Pagination offset
    limit = 240     # API fetch limit per request

    while True:
        # Build API URL with pagination
        endpoint = f"get_cases/{project_id}&suite_id={suite_id}&limit={limit}&offset={offset}"
        response = tr.client.send_get(endpoint)
        cases = response.get("cases", [])

        if not cases:
            # Break loop when no more cases are returned
            break

        all_cases.extend(cases)

        # If we receive less than the limit, it means we've reached the last page
        if len(cases) < limit:
            break

        offset += limit  # Move to next page

    logging.info(f"Total cases fetched from suite {suite_id}: {len(all_cases)}")
    return all_cases


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)  # Enable info-level logging
    tr = testrail_init()  # Initialize the TestRail client

    # Get all suites for the project and filter the ones we need
    suites = tr.get_suites(PROJECT_ID)
    suite_ids = [suite["id"] for suite in suites if suite["name"] in SUITE_NAMES]
    logging.info(f"Found suites: {suite_ids}")

    # Gather all test cases from selected suites
    all_cases = []
    for suite_id in suite_ids:
        cases = get_all_cases_from_suite(tr, PROJECT_ID, suite_id)
        all_cases.extend(cases)

    logging.info(f"Total test cases found for selected suites: {len(all_cases)}")

    updated_count = 0  # Track how many cases we updated

    # Iterate over all test cases
    for case in all_cases:
        case_id = case["id"]
        automation_status = case.get("custom_automation_status")  # Read the automation status field
        current_custom_value = case.get("custom_sub_test_suites", "Not Set")  # Read current custom field value

        logging.info(f"Case ID {case_id} custom_automation_status: {automation_status}")

        # Only proceed if the custom automation status equals 4 (4 = Completed)
        if automation_status != 4:
            logging.info(f"Skipping case {case_id} – custom_automation_status = {automation_status}")
            continue

        logging.info(
            f"Case ID {case_id} matches (custom_automation_status == 4). "
            f"Current custom_sub_test_suites: {current_custom_value}"
        )

        # Update the field if not in dry run mode
        if not DRY_RUN:
            result = tr.update_case_field(case_id, "custom_sub_test_suites", [2])
            logging.info(f"Updated case {case_id} to '[2]', Result: {result}")
        else:
            logging.info(f"[DRY RUN] Would update case {case_id} from '{current_custom_value}' to '[2]'.")

        updated_count += 1  # Count how many updates we made (or would have made)

    logging.info(f"Total cases {'updated' if not DRY_RUN else 'to be updated'}: {updated_count}")
