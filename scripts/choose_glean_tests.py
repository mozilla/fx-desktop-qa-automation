"""
Pick the glean cases a PR affects and write them as a pytest -k expression.

Writes "all" when the change can't be narrowed down, "none" when no case is affected.
"""

import ast
import json
import os
from glob import glob
from subprocess import DEVNULL, CalledProcessError, check_output

GLEAN_DIR = "tests/glean"
FLOWS_FILE = f"{GLEAN_DIR}/flows.py"
OUTPUT_FILE = "selected_glean"
# Flow decorator -> the cases.json field holding the name it registers
FLOW_DECORATORS = {"_entry": "entry", "_action": "action", "_abandonment": "action"}

BASE_BRANCH = (
    os.environ.get("GITHUB_BASE_REF") or os.environ.get("BASE_REF") or "main"
).removeprefix("refs/heads/")


def old_text(path: str) -> str | None:
    """Return the file as it is on the base branch, or None if it isn't there."""
    try:
        return check_output(
            ["git", "show", f"origin/{BASE_BRANCH}:{path}"], stderr=DEVNULL
        ).decode()
    except CalledProcessError:
        return None


def new_text(path: str) -> str | None:
    """Return the file as it is in the working tree, or None if it was removed."""
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def load_cases(path: str) -> list:
    """Return the cases in a cases.json, or [] if the file is missing."""
    text = new_text(path)
    return json.loads(text)["cases"] if text else []


def changed_case_ids(old: str | None, new: str | None) -> set | None:
    """Return the IDs of added or modified cases, or None if the whole file changed."""
    if old is None or new is None:
        return None
    old, new = json.loads(old), json.loads(new)
    if old.get("metric") != new.get("metric"):
        return None
    old_cases = {c["id"]: c for c in old["cases"]}
    return {c["id"] for c in new["cases"] if old_cases.get(c["id"]) != c}


def flow_functions(source: str) -> tuple[dict, list]:
    """Split flows.py into {function name: (code, registered flows)} and the rest."""
    functions, rest = {}, []
    for node in ast.parse(source).body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            rest.append(ast.dump(node))
            continue
        flows = {
            (FLOW_DECORATORS[d.func.id], d.args[0].value)
            for d in node.decorator_list
            if isinstance(d, ast.Call)
            and getattr(d.func, "id", None) in FLOW_DECORATORS
        }
        functions[node.name] = (ast.dump(node), flows)
    return functions, rest


def changed_flows(old: str | None, new: str | None) -> set | None:
    """Return the flows changed in flows.py, or None if anything else changed."""
    if old is None or new is None:
        return None
    old_functions, old_rest = flow_functions(old)
    new_functions, new_rest = flow_functions(new)
    if old_rest != new_rest:
        return None
    flows = set()
    for name in old_functions.keys() | new_functions.keys():
        old_fn, new_fn = old_functions.get(name), new_functions.get(name)
        if old_fn == new_fn:
            continue
        registered = (old_fn or ("", set()))[1] | (new_fn or ("", set()))[1]
        # Helpers and run_* functions can reach any case
        if not registered:
            return None
        flows |= registered
    return flows


def select_cases(changed_files: list) -> set | None:
    """Return the case IDs affected by the changed files, or None to run every case."""
    case_ids = set()
    for path in changed_files:
        # Glean tests, plus the Glean BOM and selectors in the auto_fxui package
        if "glean" not in path or not path.startswith(
            (f"{GLEAN_DIR}/", "packages/auto_fxui/")
        ):
            continue
        parts = path.split("/")
        in_metric_folder = path.startswith(f"{GLEAN_DIR}/") and len(parts) == 4
        if path == FLOWS_FILE:
            flows = changed_flows(old_text(path), new_text(path))
            if flows is None:
                return None
            for cases_file in glob(f"{GLEAN_DIR}/*/cases.json"):
                case_ids |= {
                    c["id"]
                    for c in load_cases(cases_file)
                    if any(c.get(f) == n for f, n in flows)
                }
        elif in_metric_folder and parts[3] in ("cases.json", f"test_{parts[2]}.py"):
            cases_file = f"{GLEAN_DIR}/{parts[2]}/cases.json"
            ids = None
            if parts[3] == "cases.json":
                ids = changed_case_ids(old_text(path), new_text(path))
            if ids is None:
                ids = {c["id"] for c in load_cases(cases_file)}
            case_ids |= ids
        else:
            # conftest.py, utils.py, the Glean BOM and its selectors reach every case
            return None
    return case_ids


if __name__ == "__main__":
    check_output(["git", "fetch", "--quiet", "--depth=1", "origin", BASE_BRANCH])
    git_diff_cmd = ["git", "--no-pager", "diff", "--name-only"]
    rev_hash = os.environ.get("FX_DESKTOP_QA_AUTOMATION_HEAD_REV")
    if rev_hash:
        git_diff_cmd.append(rev_hash)
    git_diff_cmd.append(f"origin/{BASE_BRANCH}")
    committed_files = check_output(git_diff_cmd).decode().splitlines()

    selected = select_cases(committed_files)
    if selected is None:
        selection = "all"
    elif not selected:
        selection = "none"
    else:
        selection = " or ".join(sorted(selected))
    print(f"Glean selection against origin/{BASE_BRANCH}: {selection}")
    with open(OUTPUT_FILE, "w") as fh:
        fh.write(selection)
