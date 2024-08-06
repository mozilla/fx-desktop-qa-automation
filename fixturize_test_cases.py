import os
import re

TEST_CASE_RE = re.compile(r'("""|#|)\s*C(\d+)')

for root, _, files in os.walk("tests"):
    for file in files:
        if file.startswith("test") and file.endswith(".py"):
            case_num = None
            filepath = os.path.join(root, file)
            script = open(filepath).readlines()
            for line in script:
                m = TEST_CASE_RE.match(line.strip())
                if not m:
                    continue
                if case_num and case_num != m[2]:
                    print(filepath)
                    print(f"Found multiple case_nums: {case_num} and {m[2]}")
                case_num = m[2]
            if case_num:
                with open("filepath", "w") as fh:
                    lines = "\n".join(
                        [
                            "",
                            "@pytest.fixture()",
                            "def test_case():",
                            f'    return "{case_num}"\n',
                            "",
                        ]
                    )
                    # fh.write("import pytest\n")
                    print("import pytest")
                    imports = True
                    for i in range(len(script)):
                        line = script[i]
                        if (
                            not (
                                len(line.strip()) == 0
                                or line.strip().startswith("'")
                                or line.strip().startswith('"')
                                or line.strip().startswith("#")
                                or line.strip().startswith("import")
                                or line.strip().startswith("from")
                            )
                            and imports
                        ):
                            # fh.write(lines)
                            print(lines)
                            imports = False
                        else:
                            # fh.write(f"{line}")
                            print(line)
                    # print(filepath)
                    # print(lines)
                    # print("-=----=-")
            else:
                print(f"Case not found for {filepath}")
