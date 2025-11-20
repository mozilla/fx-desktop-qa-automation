import os
import platform
import re
import sys
from subprocess import check_output

import yaml

CI_MANIFEST = "manifests/ci.yaml"
MANIFEST_KEY = "manifests/key.yaml"
SUPPORTED_OSES = ["mac", "win", "linux"]
HEADED_MARK = "@pytest.mark.headed"
MIN_RUN_SIZE = 7
OUTPUT_FILE = "selected_tests"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SLASH = "/" if "/" in SCRIPT_DIR else "\\"


def snakify(pascal: str) -> str:
    """Convert PascalCase to snake_case"""
    chars = pascal[0].lower()
    for c in pascal[1:]:
        if c == c.upper():
            chars = chars + f"_{c.lower()}"
        else:
            chars = chars + c
    return chars


def pascalify(snake: str) -> str:
    """Convert snake_case to PascalCase"""
    chars = snake[0].upper()
    up_flag = False
    for c in snake[1:]:
        if up_flag:
            chars = chars + c.upper()
            up_flag = False
        elif c == "_":
            up_flag = True
        else:
            chars = chars + c
    return chars


def localify(path: str) -> str:
    """Remove the script dir from an item"""
    return path.replace(SCRIPT_DIR, ".")


def get_tests_by_model(
    model_name: str, test_paths_and_contents: dict, run_list: list
) -> list:
    """
    Given a model name, a dict of paths and their file contents, and the
    list of existing tests/dirs to check, return matches by local paths
    """
    matching_tests = []
    for path, test in test_paths_and_contents.items():
        localpath = localify(path)
        in_run_list = False
        for entry in run_list:
            if entry in localpath:
                in_run_list = True
        if not in_run_list and model_name in test:
            matching_tests.append(localpath)

    return matching_tests


def dedupe(run_list: list) -> list:
    """For a run list, remove entries that are covered by more general entries."""
    run_list = list(set(run_list))
    dotslashes = []
    removes = []

    for i, entry in enumerate(run_list):
        if (
            not entry.startswith(".")
            and not entry.startswith("\\")
            and not entry.startswith("/")
        ):
            dotslashes.append(i)

    for dotslash in dotslashes:
        run_list[dotslash] = f".{SLASH}{run_list[dotslash]}"

    for i, entry_a in enumerate(run_list):
        for j, entry_b in enumerate(run_list):
            if i == j:
                continue
            candidate = max((entry_a, entry_b))
            cand_index = run_list.index(candidate)
            if entry_a in entry_b and cand_index not in removes:
                removes.append(cand_index)

    removes.sort(reverse=True)
    for remove in removes:
        del run_list[remove]

    return run_list


def sysname():
    sys_platform = platform.system().lower()
    if sys_platform.startswith("darwin"):
        return "mac"
    elif sys_platform.startswith("win"):
        return "win"
    elif sys_platform.startswith("linux"):
        return "linux"
    raise OSError("Unsupported system.")


def convert_manifest_to_list(manifest_loc):
    manifest = yaml.safe_load(open(manifest_loc))
    mkey = yaml.safe_load(open(MANIFEST_KEY))
    toplevel = [".", "tests"]
    tests = []
    if manifest:
        print(f"Reading {manifest_loc}")
    for suite in manifest:
        if suite not in mkey:
            print(f"{suite} not in {MANIFEST_KEY}")
            continue

        for testfile in manifest[suite]:
            addtest = False
            test_name = f"{testfile}.py"
            if testfile not in mkey[suite]:
                print(f"{suite}/{testfile} not in {MANIFEST_KEY}::{suite}")
                continue
            if mkey[suite][testfile] == "pass":
                addtest = True
            elif isinstance(mkey[suite][testfile], dict):
                if any([x in mkey[suite][testfile] for x in SUPPORTED_OSES]):
                    if mkey[suite][testfile][sysname()] == "pass":
                        addtest = True
                else:
                    for subtest in mkey[suite][testfile]:
                        if mkey[suite][testfile][subtest] == "pass":
                            test_name = f"{test_name}::{subtest}"
                            addtest = True
                        elif isinstance(mkey[suite][testfile][subtest], dict):
                            if sysname() in mkey[suite][testfile][subtest]:
                                if mkey[suite][testfile][subtest][sysname()] == "pass":
                                    test_name = f"{test_name}::{subtest}"
                                    addtest = True

            if addtest:
                test_to_add = SLASH.join(toplevel + [suite, test_name])
                assert os.path.exists(test_to_add.split("::")[0]), (
                    f"{test_to_add} could not be found"
                )
                tests.append(test_to_add)
                addtest = False
    return tests


if __name__ == "__main__":
    print("Selecting test set...")
    if os.path.exists(".env"):
        with open(".env") as fh:
            contents = fh.read()
            if "TESTRAIL_REPORT='true'" in contents:
                os.environ["TESTRAIL_REPORT"] = "true"
            if "RUN_ALL='true'" in contents:
                os.environ["MANUAL"] = "true"

    if os.environ.get("TESTRAIL_REPORT"):
        # Run all tests if this is a scheduled run
        run_list = convert_manifest_to_list("manifests/smoke.yaml")
        run_list = dedupe(run_list)
        with open(OUTPUT_FILE, "w") as fh:
            fh.write("\n".join(run_list))
            sys.exit(0)

    if os.environ.get("STARFOX_MANIFEST"):
        run_list = convert_manifest_to_list(os.environ["STARFOX_MANIFEST"])
        run_list = dedupe(run_list)
        with open(OUTPUT_FILE, "w") as fh:
            fh.write("\n".join(run_list))
            sys.exit(0)

    re_obj = {
        "test_re_string": r".*/.*/test_.*\.py",
        "suite_conftest_re_string": r".*/.*/conftest\.py",
        "selectors_json_re_string": r"modules/data/.*\.components\.json",
        "object_model_re_string": r"modules/.*.object.*\.py",
        "class_re_string": r"\s*class (\w+)[(A-Za-z0-9_)]*:",
    }
    for k in list(re_obj.keys()):
        if SLASH == "\\":
            re_obj[k] = re_obj.get(k).replace("/", r"\\")
        short_name = "_".join(k.split("_")[:-1])
        re_obj[short_name] = re.compile(re_obj.get(k))

    run_list = []
    check_output(["git", "fetch", "--quiet", "--depth=1", "origin", "main"])
    committed_files = (
        check_output(["git", "--no-pager", "diff", "--name-only", "origin/main"])
        .decode()
        .replace("/", SLASH)
        .splitlines()
    )

    main_conftest = "conftest.py"
    base_page = os.path.join("modules", "page_base.py")

    if main_conftest in committed_files or base_page in committed_files:
        # Run smoke tests if main conftest or basepage changed
        run_list = convert_manifest_to_list("manifests/smoke.yaml")
        run_list = dedupe(run_list)
        with open(OUTPUT_FILE, "w") as fh:
            fh.write("\n".join(run_list))
        sys.exit(0)

    all_tests = []
    test_paths_and_contents = {}
    for root, _, files in os.walk(os.path.join(SCRIPT_DIR, "tests")):
        for f in files:
            this_file = os.path.join(root, f)
            if re_obj.get("test_re").search(this_file) and "__pycache" not in this_file:
                all_tests.append(os.path.join(this_file))
                with open(this_file, encoding="utf-8") as fh:
                    lines = fh.readlines()
                    test_paths_and_contents[this_file] = "".join(lines)

    changed_suite_conftests = [
        f for f in committed_files if re_obj.get("suite_conftest_re").match(f)
    ]
    changed_selectors = [
        f for f in committed_files if re_obj.get("selectors_json_re").match(f)
    ]
    changed_models = [
        f for f in committed_files if re_obj.get("object_model_re").match(f)
    ]
    changed_tests = [f for f in committed_files if re_obj.get("test_re").match(f)]

    if changed_suite_conftests:
        run_list = [
            "." + SLASH + os.path.join(*suite.split(SLASH)[-3:-1])
            for suite in changed_suite_conftests
        ]

    if changed_selectors:
        for selector_file in changed_selectors:
            (_, filename) = os.path.split(selector_file)
            model_name = pascalify(filename.split(".")[0])
            for test_name in get_tests_by_model(
                model_name, test_paths_and_contents, run_list
            ):
                run_list.append(test_name)

    if changed_models:
        for model_file in changed_models:
            model_file_contents = "".join([line for line in open(model_file)])
            classes = re_obj.get("class_re").findall(model_file_contents)
            for model_name in classes:
                for test_name in get_tests_by_model(
                    model_name, test_paths_and_contents, run_list
                ):
                    run_list.append(test_name)

    if changed_tests:
        for changed_test in changed_tests:
            found = False
            for file in run_list:
                # Don't add if already exists in suite changes
                pieces = file.split(SLASH)
                if len(pieces) == 3 and pieces[-1] in changed_test:
                    found = True

                # Don't add if already in list
                if file in changed_test:
                    found = True
            if not found:
                run_list.append(changed_test)

    if not run_list:
        ci_paths = convert_manifest_to_list(CI_MANIFEST)
        ci_paths = dedupe(ci_paths)
        with open(OUTPUT_FILE, "w") as fh:
            fh.write("\n".join(ci_paths))
        sys.exit(0)

    if len(run_list) < MIN_RUN_SIZE:
        run_list.extend(ci_paths)

    # Dedupe just in case
    if SLASH == "\\":
        run_list = [entry.replace("/", SLASH) for entry in run_list]
    run_list = dedupe(run_list)
    run_list = [entry for entry in run_list if os.path.exists(entry.split("::")[0])]
    with open(OUTPUT_FILE, "w") as fh:
        fh.write("\n".join(run_list))
