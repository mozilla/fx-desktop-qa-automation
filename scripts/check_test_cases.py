import logging
import os

matches = {}
count = 0
# List all test suites
test_suites = [d for d in os.listdir("./tests/") if os.path.isdir(f"tests/{d}")]
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
            if not test_case.isnumeric():
                continue
        if matches.get(test_case):
            matches[test_case].append(file_name)
            logging.warning(f"Potential collision on {test_case}")
        else:
            matches[test_case] = [file_name]

dupes = [file_list for file_list in matches.values() if len(file_list) > 1]
if dupes:
    logging.warning("""|\\---/|""")
    logging.warning(
        """| o_o | Someone copied and pasted a test without changing test_case()!!!!"""
    )
    logging.warning(""" \\_^_/""")
    for dupe in dupes:
        logging.warning("=".join(dupe))
    exit(1)
