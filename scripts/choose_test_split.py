import ast
import json
import os
import re
import sys
from functools import cache
from glob import glob
from subprocess import DEVNULL, CalledProcessError, check_output

from pypom import Page

from manifests.testkey import TestKey

MANIFEST_KEY = "manifests/key.yaml"
SUPPORTED_OSES = ["mac", "win", "linux"]
HEADED_MARK = "@pytest.mark.headed"
MIN_RUN_SIZE = 7
OUTPUT_FILE = "selected_tests"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SLASH = "/" if "/" in SCRIPT_DIR else "\\"
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
IGNORE_FILE_REGEXES = [rf"\{SLASH}glean", rf"l10n_CM\{SLASH}.*\.py"]
BIG_MODELS = ["Navigation", "GenericPage", "AboutPrefs", "PanelUi"]


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
    return path.replace(ROOT_DIR, ".")


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


def model_outline(source: str) -> tuple[dict, dict]:
    """
    Split a model file into its methods ({"Class.method": code}) and the rest
    of each class ({"Class": code}, "" for module-level code, "import" for
    imports), ignoring formatting.
    """
    methods, rest = {}, {"": [], "import": []}
    for node in ast.parse(source).body:
        if isinstance(node, ast.ClassDef):
            defs = (ast.FunctionDef, ast.AsyncFunctionDef)
            for item in node.body:
                if isinstance(item, defs):
                    methods[f"{node.name}.{item.name}"] = ast.dump(item)
            node.body = [item for item in node.body if not isinstance(item, defs)]
            rest[node.name] = ast.dump(node)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            rest["import"].append(ast.dump(node))
        else:
            rest[""].append(ast.dump(node))
    return methods, rest


def changed_names(path: str) -> set | None:
    """
    Return the methods (model file) or elements (components.json) that `path`
    modifies or removes compared with main. Added ones are left out, since
    no existing test can use them. Return None if the change can't be
    narrowed down to those: a new or deleted file, other code or an import
    changed, a method the framework calls (open, loaded, __init__...) is
    changed or overridden, or a page's context or requiredForPage elements
    changed.
    """
    try:
        old = check_output(
            ["git", "show", f"origin/main:{path.replace(SLASH, '/')}"],
            stderr=DEVNULL,
        ).decode()
        with open(path, encoding="utf-8") as fh:
            new = fh.read()
        if path.endswith(".json"):
            old, new = json.loads(old), json.loads(new)
            versions = [
                v
                for k in old.keys() | new.keys()
                if old.get(k) != new.get(k)
                for v in (old.get(k), new.get(k))
                if v is not None
            ]
            if any(
                not isinstance(v, dict) or "requiredForPage" in v.get("groups", [])
                for v in versions
            ):
                return None
            names = {k for k in old if new.get(k) != old[k]}
            while True:
                children = {
                    k
                    for k, v in new.items()
                    if isinstance(v, dict) and v.get("shadowParent") in names
                }
                if children <= names:
                    return names
                names |= children
        (old_methods, old_rest) = model_outline(old)
        (new_methods, new_rest) = model_outline(new)
    except (CalledProcessError, OSError, SyntaxError, ValueError):
        return None
    if not set(old_rest.pop("import")) <= set(new_rest.pop("import")):
        return None
    if any(new_rest.get(k) != v for k, v in old_rest.items()):
        return None
    changed = {
        name
        for name in old_methods.keys() | new_methods.keys()
        if old_methods.get(name) != new_methods.get(name)
        and name.split(".")[0] in old_rest
        and name.split(".")[0] not in BIG_MODELS
    }
    if any(name.split(".")[1] in framework_methods() for name in changed):
        return None
    return {name.split(".")[1] for name in changed if name in old_methods}


@cache
def framework_methods() -> set:
    """Names of BasePage and pypom Page methods, which tests reach implicitly."""
    with open(os.path.join("modules", "page_base.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    return set(dir(Page)) | {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


@cache
def function_references() -> dict:
    """Map each function in modules/ to the names and strings it uses."""
    references = {}
    for path in glob(os.path.join("modules", "**", "*.py"), recursive=True):
        with open(path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                refs = references.setdefault(node.name, set())
                for n in ast.walk(node):
                    if isinstance(n, ast.Attribute):
                        refs.add(n.attr)
                    elif isinstance(n, ast.Name):
                        refs.add(n.id)
                    elif isinstance(n, ast.Constant) and isinstance(n.value, str):
                        refs.add(n.value)
    return references


@cache
def conftest_contents() -> dict:
    """Map each suite's conftest.py, and the root one, to its contents."""
    contents = {}
    for conftest in glob(os.path.join("tests", "*", "conftest.py")) + ["conftest.py"]:
        with open(conftest, encoding="utf-8") as fh:
            contents[conftest] = fh.read()
    return contents


def get_tests_by_change(path: str, test_paths_and_contents: dict) -> list | None:
    """
    Return the tests, or suites through their conftest.py, that use a method
    or element changed in `path`, directly or through other functions in
    modules/. Return None to fall back to every test using the model: when
    the change can't be narrowed down, a changed name is never used by name
    (built at runtime, or called by the framework, like __init__), or the
    root conftest.py uses it.
    """
    names = changed_names(path)
    if names is None:
        return None
    if not names:
        return []

    references = function_references()
    affected = set(names)
    while True:
        callers = {f for f, refs in references.items() if refs & affected}
        if callers <= affected:
            break
        affected |= callers

    def name_re(name_set: set) -> re.Pattern:
        alternatives = "|".join(re.escape(n) for n in sorted(name_set))
        return re.compile(rf"(?<!\w)(?:{alternatives})(?!\w)")

    conftests = dict(conftest_contents())
    all_contents = "\n".join([*test_paths_and_contents.values(), *conftests.values()])
    used_in_modules = set().union(*references.values())
    if any(not name_re({n}).search(all_contents) for n in names - used_in_modules):
        return None
    uses_affected = name_re(affected).search
    if uses_affected(conftests.pop("conftest.py")):
        return None

    tests = [
        localify(test)
        for test, content in test_paths_and_contents.items()
        if uses_affected(content)
    ]
    suites = [
        f".{SLASH}{os.path.dirname(conftest)}"
        for conftest, content in conftests.items()
        if uses_affected(content)
    ]
    return tests + suites


def get_tests_in_suite(path: str):
    """Get all the test paths in a suite dir"""
    return [
        SLASH.join([path, n])
        for n in os.listdir(path)
        if n.startswith("test_") and n.endswith(".py")
    ]


def dedupe(run_list: list) -> list:
    """For a run list, remove entries that are covered by more general entries."""
    run_list = list(set(run_list))
    dotslashes = []
    removes = []
    adds = []

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
        if not os.path.exists(entry_a.split("::")[0]):
            print(f"Removing {entry_a}: path does not exist")
            removes.append(i)
            continue
        elif os.path.isdir(entry_a):
            print(f"Removing {entry_a}: is a directory, adding tests")
            removes.append(i)
            adds.extend(get_tests_in_suite(entry_a))
            continue
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
    run_list.extend(adds)

    run_list.sort()
    return run_list


if __name__ == "__main__":
    manifest = TestKey(MANIFEST_KEY)

    category = os.environ.get("STARFOX_CATEGORY")
    if category:
        category = category.lower()
        split_name = os.environ.get("STARFOX_SPLIT", "all")

        # platform MUST be set by the job environment (win|mac|linux)
        platform = os.environ.get("STARFOX_PLATFORM")
        if not platform:
            raise SystemExit(
                "STARFOX_PLATFORM must be set to 'win', 'mac', or 'linux' when STARFOX_CATEGORY is used."
            )

        platform = platform.lower()
        if platform not in SUPPORTED_OSES:
            raise SystemExit(
                f"Unsupported STARFOX_PLATFORM: '{platform}'. Expected one of: {', '.join(SUPPORTED_OSES)}."
            )

        print(
            f"Gathering tests from split '{split_name}', category '{category}', platform '{platform}'..."
        )

        # Call gather_category with platform explicitly
        run_list = manifest.gather_category(
            split_name=split_name, platform=platform, category=category
        )
        run_list = dedupe(run_list)

        with open(OUTPUT_FILE, "w") as fh:
            fh.write("\n".join(run_list))
        sys.exit(0)

    print("Selecting test set...")
    if os.environ.get("STARFOX_SPLIT"):
        print(f"Gathering tests from split: {os.environ['STARFOX_SPLIT']}...")
        run_list = manifest.gather_split(os.environ["STARFOX_SPLIT"])
        run_list = dedupe(run_list)
        run_list = manifest.filter_filenames_by_pass(run_list)

        # Assign a split name to STARFOX_EXCLUDE to remove tests in that split from run
        exclusions = os.environ.get("STARFOX_EXCLUDE")
        if exclusions:
            for excluded_split in exclusions.split(","):
                print(f"Excluding tests from split: {excluded_split}...", end="")
                exclude_count = 0
                for exclude in dedupe(manifest.gather_split(excluded_split)):
                    if exclude in run_list:
                        exclude_count += 1
                        run_list.remove(exclude)
                print(f"excluded {exclude_count} entries.")

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
    git_diff_cmd = ["git", "--no-pager", "diff", "--name-only"]
    rev_hash = os.environ.get("FX_DESKTOP_QA_AUTOMATION_HEAD_REV")
    if rev_hash:
        git_diff_cmd.append(rev_hash)
    git_diff_cmd.append("origin/main")
    committed_files = (
        check_output(git_diff_cmd).decode().replace("/", SLASH).splitlines()
    )

    # Never select tests that work in a different flow
    # TODO: fully move glean out of the main starfox flow, like l10n
    for reg in [re.compile(ignore) for ignore in IGNORE_FILE_REGEXES]:
        committed_files = [f for f in committed_files if reg.search(f) is None]

    print("Committed files:\n\t", end="")
    print("\n\t".join(committed_files))

    main_conftest = "conftest.py"
    base_page = os.path.join("modules", "page_base.py")
    run_list = []

    if main_conftest in committed_files or base_page in committed_files:
        # Run additional tests if main conftest or basepage changed
        run_list.extend(manifest.gather_split("ci-extended"))
        run_list = dedupe(run_list)

    all_tests = []
    test_paths_and_contents = {}
    for root, _, files in os.walk(os.path.join(ROOT_DIR, "tests")):
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
        run_list.extend(
            [
                "." + SLASH + os.path.join(*suite.split(SLASH)[-3:-1])
                for suite in changed_suite_conftests
            ]
        )

    if changed_selectors:
        for selector_file in changed_selectors:
            (_, filename) = os.path.split(selector_file)
            model_name = pascalify(filename.split(".")[0])
            if model_name in BIG_MODELS:
                continue  # some models are too big to run all tests
            tests = get_tests_by_change(selector_file, test_paths_and_contents)
            if tests is None:
                tests = get_tests_by_model(
                    model_name, test_paths_and_contents, run_list
                )
            run_list.extend(tests)

    if changed_models:
        for model_file in changed_models:
            # When we remove a file, it appears in the git diff, but not in real life
            if not os.path.exists(model_file):
                continue
            tests = get_tests_by_change(model_file, test_paths_and_contents)
            if tests is not None:
                run_list.extend(tests)
                continue
            model_file_contents = "".join([line for line in open(model_file)])
            classes = re_obj.get("class_re").findall(model_file_contents)
            for model_name in classes:
                if model_name in BIG_MODELS:
                    continue  # model too big, don't run all tests
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

    ci_paths = manifest.gather_split("ci")
    ci_paths = dedupe(ci_paths)
    if not run_list:
        with open(OUTPUT_FILE, "w") as fh:
            fh.write("\n".join(ci_paths))
        sys.exit(0)

    run_list.extend(ci_paths)

    # Dedupe just in case
    if SLASH == "\\":
        run_list = [entry.replace("/", SLASH) for entry in run_list]
    run_list = [entry for entry in run_list if os.path.exists(entry)]
    run_list = dedupe(run_list)
    run_list = manifest.filter_filenames_by_pass(run_list)
    run_list = [entry for entry in run_list if os.path.exists(entry.split("::")[0])]
    with open(OUTPUT_FILE, "w") as fh:
        fh.write("\n".join(run_list))
