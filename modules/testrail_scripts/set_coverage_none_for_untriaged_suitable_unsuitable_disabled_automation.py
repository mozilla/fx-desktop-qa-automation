import logging
import os
import time

from dotenv import load_dotenv

from modules.testrail_integration import testrail_init

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Load env file from project root
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
env_file_path = os.path.join(project_root, "testrail_credentials.env")
load_dotenv(dotenv_path=env_file_path)

# TestRail project ID (Fx Desktop)
PROJECT_ID = 17

# Automation status values
AUTOMATION_STATUS = {
    "UNTRIAGED": 1,
    "SUITABLE": 2,
    "NOT_SUITABLE": 3,
    "COMPLETED": 4,
    "DISABLED": 5,
}

# Automation coverage values
AUTOMATION_COVERAGE = {"NONE": 1, "PARTIAL": 2, "FULL": 3}

# Coverage value to name mapping for better logging
COVERAGE_NAMES = {1: "None", 2: "Partial", 3: "Full"}

# Status value to name mapping for better logging
STATUS_NAMES = {
    1: "Untriaged",
    2: "Suitable",
    3: "Unsuitable",
    4: "Completed",
    5: "Disabled",
}


def get_all_suites(tr, project_id):
    """Get all suites from the project"""
    suites = tr.client.send_get(f"get_suites/{project_id}")
    logging.info(f"Found {len(suites)} suites in project {project_id}")
    return suites


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

    return all_cases


def update_coverage_to_none(tr, project_id, dry_run=True, batch_size=25):
    """
    Set automation coverage to None for all test cases that have automation status of
    Untriaged, Suitable, or Not Suitable, regardless of their current coverage value
    """
    start_time = time.time()
    try:
        # Track statistics
        total_cases_to_update = 0
        skipped_cases = 0
        updated_count = 0
        changed_case_ids = []  # Track all case IDs that will be changed

        # Get all suites in the project
        suites = get_all_suites(tr, project_id)
        total_suites = len(suites)

        # Process each suite
        for index, suite in enumerate(suites, 1):
            suite_id = suite["id"]
            suite_name = suite["name"]
            logging.info(f"Processing suite {index}/{total_suites}: {suite_name}")

            try:
                cases = get_all_test_cases(tr, project_id, suite_id)

                # Filter cases that need updating
                update_targets = []
                for case in cases:
                    status = case.get("custom_automation_status")
                    coverage = case.get("custom_automation_coverage")

                    # Check if status is one that should have None coverage
                    if status in [
                        AUTOMATION_STATUS["UNTRIAGED"],
                        AUTOMATION_STATUS["SUITABLE"],
                        AUTOMATION_STATUS["NOT_SUITABLE"],
                        AUTOMATION_STATUS["DISABLED"],
                    ]:
                        # If coverage is not None, add to update targets
                        if coverage != AUTOMATION_COVERAGE["NONE"]:
                            update_targets.append(case)
                        else:
                            skipped_cases += 1

                suite_update_count = len(update_targets)
                total_cases_to_update += suite_update_count

                if suite_update_count > 0:
                    logging.info(
                        f"Found {suite_update_count} cases to update in '{suite_name}'"
                    )

                    # Update in batches
                    for i in range(0, len(update_targets), batch_size):
                        batch = update_targets[i : i + batch_size]

                        if not dry_run:
                            # Process batch updates
                            batch_ids = []
                            for case in batch:
                                case_id = case["id"]
                                current_coverage = case.get(
                                    "custom_automation_coverage"
                                )
                                coverage_name = COVERAGE_NAMES.get(
                                    current_coverage, "Empty"
                                )

                                try:
                                    tr.update_case_field(
                                        case_id,
                                        "custom_automation_coverage",
                                        str(AUTOMATION_COVERAGE["NONE"]),
                                    )
                                    batch_ids.append(case_id)
                                    changed_case_ids.append((case_id, suite_name))
                                    updated_count += 1
                                except Exception as e:
                                    logging.error(f"Error updating case {case_id}: {e}")

                            if batch_ids:
                                logging.info(
                                    f"Updated batch of {len(batch_ids)} cases to None coverage"
                                )
                        else:
                            # Log all cases in dry run mode
                            logging.info(
                                f"Would update batch of {len(batch)} cases to None coverage"
                            )
                            for case in batch:
                                case_id = case["id"]
                                current_status = case.get("custom_automation_status")
                                current_coverage = case.get(
                                    "custom_automation_coverage"
                                )
                                status_name = STATUS_NAMES.get(
                                    current_status, "Unknown"
                                )
                                coverage_name = COVERAGE_NAMES.get(
                                    current_coverage, "Empty"
                                )
                                logging.info(
                                    f"  Case {case_id} - Status: {status_name}, Coverage: {coverage_name} → None"
                                )
                                changed_case_ids.append((case_id, suite_name))

            except Exception as e:
                logging.error(f"Error processing suite {suite_id}: {e}")
                continue

        # Calculate execution time
        execution_time = time.time() - start_time

        # Log summary
        logging.info("\n=== EXECUTION SUMMARY ===")
        logging.info(f"Total cases to update: {total_cases_to_update}")
        logging.info(f"Cases skipped (already None): {skipped_cases}")

        if not dry_run:
            logging.info(f"Cases successfully updated: {updated_count}")
        else:
            logging.info(
                f"Cases that would be updated (dry run): {total_cases_to_update}"
            )

        logging.info(f"Execution time: {execution_time:.2f} seconds")
        if total_suites > 0:
            logging.info(
                f"Average time per suite: {execution_time / total_suites:.2f} seconds"
            )
        if updated_count > 0:
            logging.info(
                f"Average time per update: {execution_time / updated_count:.2f} seconds"
            )

    except Exception as e:
        logging.error(f"Error in overall process: {e}")


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
    update_coverage_to_none(tr, PROJECT_ID, dry_run)


if __name__ == "__main__":
    main()
