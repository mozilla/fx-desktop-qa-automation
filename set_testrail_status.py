import os
import sys

import yaml

from modules import testrail as tr
from modules.testrail import TestRail

FX_DESKTOP_PROJECT_ID = 17
DOTENV = ".env"


def testrail_init() -> TestRail:
    """Connect to a TestRail API session"""
    local = os.environ.get("TESTRAIL_BASE_URL").split("/")[2].startswith("127")
    tr_session = tr.TestRail(
        os.environ.get("TESTRAIL_BASE_URL"),
        os.environ.get("TESTRAIL_USERNAME"),
        os.environ.get("TESTRAIL_API_KEY"),
        local,
    )
    return tr_session


if __name__ == "__main__":
    with open(DOTENV) as fh:
        env = yaml.safe_load(fh)
    for key, val in env.items():
        print(f"Getting value for {key}")
        os.environ[key] = val
    tr = testrail_init()
    # Assume the suite numbers are given as command-line arguments
    for suite_num in [int(s) for s in sys.argv[1:]]:
        print(f"working on suite: {suite_num}")
        cases_in_suite = tr._get_test_cases(FX_DESKTOP_PROJECT_ID, suite_num).get(
            "cases"
        )
        completed_cases = [
            case_
            for case_ in cases_in_suite
            if case_.get("custom_automation_status") == 4
        ]
        for case_ in completed_cases:
            print(case_.get("id"), "set to full")
            tr.update_test_case(case_.get("id"), custom_automation_coverage=3)
