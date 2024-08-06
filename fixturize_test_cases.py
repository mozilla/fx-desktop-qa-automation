import os
import re

TEST_CASE_RE = re.compile(r'("""|#|)\s*C(\d+)')

for root, _, files in os.walk("tests"):
    for file in files:
        if file.startswith("test") and file.endswith(".py"):
            found = False
            for line in open(os.path.join(root, file)).readlines():
                m = TEST_CASE_RE.match(line.strip())
                if not m:
                    continue
                found = True
            if not found:
                print(f"Case not found for {os.path.join(root, file)}")
