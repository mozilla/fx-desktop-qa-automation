import os
from ast import literal_eval

from modules import testrail_integration as tri
from modules.testrail import APIError as TestRailAPIError

seen = []
tr_session = tri.testrail_init()
print("Validating test cases...")
test_suites = [d for d in os.listdir("./tests/") if os.path.isdir(f"./tests/{d}")]
for test_suite in test_suites:
    conftest = f"tests/{test_suite}/conftest.py"
    with open(conftest) as f:
        for line in f:
            if line.strip().startswith("def suite_id():"):
                break
        suite_info = literal_eval(f.readline().strip().split(" ", 1)[1])
        print(test_suite, suite_info)
    suite_id = suite_info[0].replace("S", "")
    print(f"Checking {suite_id}")
    cases = []
    end_of_batch = False
    offset = 0
    while not end_of_batch:
        try:
            cases_info = tr_session.get_cases_in_suite(17, suite_id, offset)
            these_cases = cases_info.get("cases", None)
        except TestRailAPIError:
            print(f"{suite_id} is not a valid suite id, skipping...")
            end_of_batch = True
            continue
        if these_cases is None:
            print(f"No cases match {suite_id}.")
            end_of_batch = True
            continue
        cases.extend(these_cases)
        if cases_info.get("size") == 250:
            offset += 250
            if offset == 250:
                offset = 249
        else:
            end_of_batch = True

    case_ids = [c.get("id") for c in cases]

    for test in os.listdir(f"./tests/{test_suite}"):
        if test[0:4] != "test":
            continue
        # Find tests and parse test case number
        file_name = f"tests/{test_suite}/{test}"
        with open(file_name) as f:
            for line in f:
                if line.startswith("def test_case():"):
                    break
            line = f.readline().strip()
            ind = line.find('"') + 1
            test_case = line[ind:-1]
            if test_case in seen:
                continue
            seen.append(test_case)
            try:
                int(test_case)
            except ValueError:
                print(f"{test_case} is not a valid test case, skipping...")
                print(f"See {file_name}")
                continue
            if int(test_case) not in case_ids:
                print(f"Test case {test_case} does not exist in suite {suite_id}")
                print(f"See {file_name}")
                try:
                    this_case = tr_session.get_test_case(test_case)
                    print(
                        f"Test belongs to suite {this_case.get('suite_id', '<Missing>')}"
                    )
                except TestRailAPIError:
                    print("This test case does not exist.")
                    continue
