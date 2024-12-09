import logging
import os

d = {}
count = 0
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
            ind = line.find('"') + 1
            test_case = line[ind:-1]
        if d.get(test_case):
            count += 1
        else:
            d[test_case] = file_name

if count > 2:
    logging.warning("""|\---/|""")
    logging.warning(
        """| o_o | Someone copied and pasted a test without changing test_case()!!!!"""
    )
    logging.warning(""" \_^_/""")
    exit(1)
