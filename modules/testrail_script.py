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
env_file_path = os.path.join(project_root, "api_credentials.env")
load_dotenv(dotenv_path=env_file_path)

MY_SUITES = ["Printing UI", "Profile", "Reader View"]
PROJECT_ID = 17

DRY_RUN = True  # Set to False when performing actual run

def main():
    # Read credentials from environment
    base_url = os.environ.get("TESTRAIL_BASE_URL")
    username = os.environ.get("TESTRAIL_USERNAME")
    api_key = os.environ.get("TESTRAIL_API_KEY")

    if not all([base_url, username, api_key]):
        logging.error("Missing TestRail credentials. Check your .env file.")
        return

    logging.info(f"Loaded TestRail credentials for user: {username}")
    logging.info(f"TestRail Base URL: {base_url}")

    tr = testrail_init()

    logging.info(f"Fetching suite IDs for suites: {MY_SUITES}")
    suites = list(tr.get_suites(PROJECT_ID))
    suite_ids = [
        suite["id"]
        for suite in suites
        if suite["name"] in MY_SUITES
    ]
    logging.info(f"Suite IDs to process: {suite_ids}")

    case_ids = []
    for suite_id in suite_ids:
        val = tr._get_test_cases(PROJECT_ID, suite_id)
        if val["size"] < val["limit"]:
            matching_cases = [
                case for case in val["cases"] if case["custom_automated_test_names"]
            ]
            matching_case_ids = [case["id"] for case in matching_cases]

            if DRY_RUN:
                logging.info(
                    f"[DRY RUN] Suite {suite_id} would process cases: {matching_case_ids}"
                )
            else:
                case_ids.extend(matching_case_ids)
                logging.info(
                    f"Suite {suite_id} processed and added case IDs: {matching_case_ids}"
                )
        else:
            logging.warning(f"Suite {suite_id} test cases exceed retrieval limit.")

    if DRY_RUN:
        logging.info("[DRY RUN] No actual updates performed.")
        logging.info(f"[DRY RUN] Total collected case IDs (not updated): {case_ids}")
    else:
        logging.info(f"Total collected case IDs: {case_ids}")
        # Add here actual logic for updates if necessary

if __name__ == "__main__":
    main()