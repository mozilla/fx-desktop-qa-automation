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

# TestRail project ID (Fx Desktop)
PROJECT_ID = 17


def get_all_suites(tr, project_id):
    """Get all suites from the project"""
    suites = tr.client.send_get(f"get_suites/{project_id}")
    logging.info(f"Found {len(suites)} suites in project {project_id}")
    return suites


# Set limit below maximum value as a precaution to avoid API errors
def get_all_test_cases(tr, project_id, suite_id):
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


def update_null_automation_status(tr, project_id, dry_run=True):
    """Update test cases with None automation status to Untriaged"""
    try:
        # Get all suites in the project
        suites = get_all_suites(tr, project_id)

        # Track statistics
        total_null_cases = 0
        updated_count = 0

        # Process each suite
        for suite in suites:
            suite_id = suite["id"]
            suite_name = suite["name"]
            logging.info(f"Processing suite {suite_name} (ID: {suite_id})...")

            # Retrieve test cases for this suite
            try:
                cases = get_all_test_cases(tr, project_id, suite_id)

                # Filter cases with null automation status
                null_status_cases = [
                    case
                    for case in cases
                    if case.get("custom_automation_status") is None
                ]

                suite_null_count = len(null_status_cases)
                total_null_cases += suite_null_count

                logging.info(
                    f"Found {suite_null_count} cases with null automation status in suite {suite_name}"
                )

                # Update each case that meets the criteria
                for case in null_status_cases:
                    case_id = case["id"]
                    try:
                        if dry_run:
                            logging.info(
                                f"[DRY RUN] Would update case {case_id}: set automation status to Untriaged (1)"
                            )
                        else:
                            # Perform the update
                            tr.update_case_field(
                                case_id, "custom_automation_status", "1"
                            )
                            logging.info(
                                f"Updated case {case_id}: set automation status to Untriaged (1)"
                            )
                            updated_count += 1
                    except Exception as e:
                        logging.error(f"Error updating case {case_id}: {e}")
            except Exception as e:
                logging.error(f"Error processing suite {suite_id}: {e}")
                continue

        # Log summary
        logging.info(
            f"Summary: Found {total_null_cases} cases with null automation status across all suites"
        )
        if not dry_run:
            logging.info(f"Updated {updated_count} cases to Untriaged")
        else:
            logging.info(
                f"Would update {total_null_cases} cases to Untriaged (dry run)"
            )

    except Exception as e:
        logging.error(f"Error processing cases: {e}")


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

    # Process all cases in the project
    logging.info(f"Processing project ID: {PROJECT_ID}...")
    update_null_automation_status(tr, PROJECT_ID, dry_run)


if __name__ == "__main__":
    main()
