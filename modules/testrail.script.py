import logging
import os

from dotenv import load_dotenv

from modules.testrail_integration import testrail_init

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load env file from project root
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, ".."))
env_file_path = os.path.join(project_root, "testrail_credentials.env")
load_dotenv(dotenv_path=env_file_path)

# Suite Name -> (Suite ID, Custom Field Name, New Value ("full"))
SUITE_MAPPING = {
    "Address Bar and Search": (18215, "custom_automation_coverage", 3),
    "Audio Video": (1731, "custom_automation_coverage", 3),
    "Downloads": (29219, "custom_automation_coverage", 3),
}

# TestRail project ID (Fx Desktop)
PROJECT_ID = 17


def update_starfox_cases(tr, project_id, suite_id, field_id, new_value, dry_run=True):
    """Fetch automated test cases (based on the "completed" - 4 status) from a TestRail suite and update a custom
    field to a new value "full" - 3."""
    try:
        response = tr.get_test_cases(project_id, suite_id)
        cases = response.get("cases", [])
        # Filter cases
        starfox_cases = []

        for case in cases:
            if (
                case.get("custom_automated_test_names")
                and case.get("custom_automation_status") == 4
            ):
                starfox_cases.append(case)

        logging.info(
            f"Found {len(starfox_cases)} STARfox automated test cases in suite {suite_id}."
        )

        # Update each case that meets the criteria
        for case in starfox_cases:
            case_id = case["id"]
            if dry_run:
                logging.info(
                    f"[DRY RUN] Would update case {case_id}: set {field_id} to {new_value}."
                )
            else:
                # Perform the update
                tr.update_case_field(case_id, field_id, new_value)
                logging.info(f"Updated case {case_id}: set {field_id} to {new_value}.")
    except Exception as e:
        logging.error(f"Error processing suite {suite_id}: {e}")


def main():
    # Read credentials from environment
    base_url = os.environ.get("TESTRAIL_BASE_URL")
    username = os.environ.get("TESTRAIL_USERNAME")
    api_key = os.environ.get("TESTRAIL_API_KEY")

    if not all([base_url, username, api_key]):
        logging.error("Missing TestRail credentials. Check your .env file.")
        return

    logging.info(f"Loaded credentials for user: {username}")
    logging.info(f"Base URL: {base_url}")

    tr = testrail_init()

    # Safe approach to not accidentally update cases
    dry_run = True

    # Iterate over all mapped suites and apply update
    for suite_name, (suite_id, field_id, new_value) in SUITE_MAPPING.items():
        logging.info(f"Processing suite '{suite_name}' (ID: {suite_id})...")
        update_starfox_cases(tr, PROJECT_ID, suite_id, field_id, new_value, dry_run)


if __name__ == "__main__":
    main()
