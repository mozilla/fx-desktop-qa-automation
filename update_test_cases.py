import os, logging
import modules.testrail_integration as tri

SUITES = ["Form Autofill", "Geolocation", "Language Packs"]
FULL_COVERAGE_VALUE = 3


def main():
    # Set env variables for testrail_init function
    os.environ["TESTRAIL_BASE_URL"] = "https://mozilla.testrail.io"
    os.environ["TESTRAIL_USERNAME"] = "user"
    os.environ["TESTRAIL_API_KEY"] = "api_key"
    tr = tri.testrail_init()

    # Get all suites from our project
    for suite in tr.get_suites(17):
        if suite["name"] not in SUITES:
            continue
        # Loop through all the test cases in the target suite
        for case in tr._get_test_cases(17, suite["id"])["cases"]:
            # Check if the custom automated field is set to see if we automated it
            if case["custom_automated_test_names"]:
                logging.info(f"Updating test case {case['id']} coverage status for full")
                tr.update_case_field(case['id'], "custom_automation_coverage", FULL_COVERAGE_VALUE)


if __name__ == "__main__":
    main()
