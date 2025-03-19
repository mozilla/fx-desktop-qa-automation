import logging
import os

from modules.testrail_integration import testrail_init

MY_SUITES = ["Menus", "Networking", "Notifications, Push Notifications and Alerts"]
PROJECT_ID = 17

if __name__ == "__main__":
    os.environ["TESTRAIL_BASE_URL"] = "https://mozilla.testrail.io"
    os.environ["TESTRAIL_USERNAME"] = "payalew@mozilla.com"
    os.environ["TESTRAIL_API_KEY"] = "WNl7Py3VoWq1yjsVH/Qb-4ypBk/VqBR//JF4hLg9i"
    tr = testrail_init()

    # get suite ids for our project
    suite_ids = map(
        lambda d: d["id"],
        filter(lambda d: d["name"] in MY_SUITES, tr.get_suites(PROJECT_ID)),
    )

    # get all the case Ids in the given suite.
    case_ids = []
    for suite_id in suite_ids:
        val = tr._get_test_cases(17, suite_id)
        # check that pulled result is all the test cases for the suite.
        if val["size"] < val["limit"]:
            case_ids.extend(
                map(
                    lambda d: d["id"],
                    filter(lambda d: d["custom_automated_test_names"], val["cases"]),
                )
            )
        else:
            logging.warning(f"Suite {suite_id} test cases over limit.")

    # Update automation_coverage value for each case id.
    # for case_id in case_ids:
    #     tr.update_case_field(case_id, "custom_automation_coverage", 3)
