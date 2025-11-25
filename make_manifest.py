import os
import re

import yaml

TESTFILE_RE = re.compile(r"test_.*\.py")
TEST_RE = re.compile(r"def (test.*)\(")

if __name__ == "__main__":
    testdict = {}
    for root, _, files in os.walk("tests"):
        for f in files:
            if not TESTFILE_RE.match(f):
                continue
            pointer = testdict
            for level in os.path.split(root)[1:]:
                if level not in testdict:
                    pointer[level] = {}
                pointer = pointer[level]
            status = "pass"
            filename = os.path.join(root, f)
            with open(filename) as fh:
                metatest = f.rsplit(".", 1)[0]
                for line in fh.readlines():
                    m = TEST_RE.search(line)
                    if m and m[1] != "test_case":
                        if metatest not in pointer:
                            pointer[metatest] = {m[1]: status}
                        else:
                            pointer[metatest][m[1]] = status
                        print(yaml.safe_dump(testdict), "\n\n\n\n===\n\n\n\n")
                    status = "pass"
                    if "mark.unstable" in line:
                        status = "unstable"
    with open("new_manifest.yaml", "w") as fh:
        yaml.safe_dump(testdict, fh)
