import os
import re
import sys
from subprocess import check_output

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CI_MARK = "@pytest.mark.ci"
HEADED_MARK = "@pytest.mark.headed"


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


if __name__ == "__main__":
    if os.path.exists(".env"):
        with open(".env") as fh:
            if "TESTRAIL_REPORT='true'" in fh.read():
                os.environ["TESTRAIL_REPORT"] = "true"

    if os.environ.get("TESTRAIL_REPORT"):
        # Run all tests if this is a scheduled beta
        print(".")
        sys.exit(0)

    slash = "/" if "/" in SCRIPT_DIR else "\\"

    re_obj = {
        "test_re_string": r"tests/.*/test_.*\.py",
        "suite_conftest_re_string": r"tests/.*/conftest\.py",
        "selectors_json_re_string": r"modules/data/.*\.components\.json",
        "object_model_re_string": r"modules/.*.object.*\.py",
        "class_re_string": r"\s*class (\w+):",
    }
    for k in list(re_obj.keys()):
        if slash == "\\":
            re_obj[k] = re_obj.get(k).replace("/", r"\\")
        short_name = "_".join(k.split("_")[:-1])
        re_obj[short_name] = re.compile(re_obj.get(k))

    run_list = []
    check_output(["git", "fetch", "--quiet", "--depth=1", "origin", "main"])
    committed_files = (
        check_output(["git", "--no-pager", "diff", "--name-only", "origin/main"])
        .decode()
        .replace("/", slash)
        .splitlines()
    )

    main_conftest = os.path.join(SCRIPT_DIR, "conftest.py")
    base_page = os.path.join(SCRIPT_DIR, "modules", "page_base.py")

    if main_conftest in committed_files or base_page in committed_files:
        # Run all the tests (no files as arguments) if main conftest or basepage changed
        print(".")
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

    ci_paths = []
    for path, content in test_paths_and_contents.items():
        if CI_MARK in content:
            ci_paths.append(localify(path))

    # Dedupe just in case
    ci_paths = list(set(ci_paths))

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
            os.path.join(*suite.split(slash)[-3:-1])
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
                if file in changed_test:
                    found = True
            if not found:
                run_list.append(changed_test)

    if not run_list:
        print("\n".join(ci_paths))
    else:
        run_list.extend(ci_paths)

        # Dedupe just in case
        run_list = list(set(run_list))
        print("\n".join(run_list))
