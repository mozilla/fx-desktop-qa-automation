import json
import logging

from modules.testrail_integration import testrail_init

# from dotenv import load_dotenv
#
# load_dotenv()

MY_SUITES = ["Menus", "Networking", "Notifications, Push Notifications and Alerts"]
PROJECT_ID = 17

if __name__ == "__main__":
    tr = testrail_init()

    # get suite ids for our project
    suite_ids = map(
        lambda d: d["id"],
        filter(lambda d: d["name"] in MY_SUITES, tr.get_suites(PROJECT_ID)),
    )

    # get all the case Ids in the given suite.
    case_ids = []
    case_entries = []
    for suite_id in suite_ids:
        val = tr._get_test_cases(17, suite_id)
        # check that pulled result is all the test cases for the suite.
        if val["size"] < val["limit"]:
            cases = list(
                filter(
                    lambda d: d["custom_automated_test_names"]
                    and d["custom_automation_status"] == 4,
                    val["cases"],
                )
            )
            case_entries.extend(cases)
            case_ids.extend(
                map(
                    lambda d: d["id"],
                    cases,
                )
            )
        else:
            logging.warning(f"Suite {suite_id} test cases over limit.")
    # Dump changed case entries
    # with open('script_result.json', 'w+') as f:
    #     json.dump(case_entries, f, indent=4)
    # Update automation_coverage value for each case id.
    # for case_id in case_ids:
    #     tr.update_case_field(case_id, "custom_automation_coverage", 3)
