import modules.testrail_integration as tri
from modules.testrail import TestRail, APIClient
import os

d = {}
# List all test suites
test_suites = [d for d in os.listdir("./tests/")]
for test_suite in test_suites:
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
            ind = line.find('"')+1
            test_case = line[ind:-1]
        if d.get(test_case):
            print(d[test_case], file_name)
        else:
            d[test_case] = file_name


# tr = tri.testrail_init()
# print(tr.client.send_get("get_case_fields/"))
# print(tr.get_custom_field())
# tr.get_test_case(test_case)
# data = {
#     "Automated Test Name(s)": "",
#     "Sub Test Suite(s)": ""
# }
# tr.update_existing_test_case(test_case, data)


    