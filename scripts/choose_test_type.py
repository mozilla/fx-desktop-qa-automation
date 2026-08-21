import json
import os
import re
import sys
from subprocess import check_output

# Glean is not here on purpose: a page_base.py change should not trigger it
ALL_TEST_TYPES = ["starfox", "l10n"]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SLASH = "/" if "/" in SCRIPT_DIR else "\\"

file_subsets = {
    "starfox": ["modules/data", "modules/page", "modules/browser", "tests/"],
    "l10n": ["l10n_CM/"],
}

# Checked before file_subsets, so glean files never also select starfox
glean_subset = [
    os.path.join("tests", "glean") + SLASH,
    os.path.join("modules", "browser_object_glean.py"),
    os.path.join("modules", "data", "glean.components.json"),
]

l10n_module_patterns = [
    r"modules/page_object_autofill\.py",
    r"modules/data/address_fill\.components\.json",
    r"modules/browser_object_autofill_popup\.py",
]

l10n_module_patterns = set(
    [
        re.compile(val.replace("/", r"\\")) if SLASH == "\\" else re.compile(val)
        for val in l10n_module_patterns
    ]
)

if len(sys.argv) > 1:
    print(sys.argv[1:])
    sys.exit(0)

check_output(["git", "fetch", "--quiet", "--depth=1", "origin", "main"])

git_diff_cmd = ["git", "--no-pager", "diff", "--name-only"]
rev_hash = os.environ.get("FX_DESKTOP_QA_AUTOMATION_HEAD_REV")
if rev_hash:
    git_diff_cmd.append(rev_hash)
git_diff_cmd.append("origin/main")
committed_files = check_output(git_diff_cmd).decode().replace("/", SLASH).splitlines()
base_page = os.path.join("modules", "page_base.py")

test_types = set()

if base_page in committed_files:
    print(ALL_TEST_TYPES)
    sys.exit()

for f in committed_files:
    if any([r.match(f) for r in l10n_module_patterns]):
        print(ALL_TEST_TYPES)
        sys.exit()

    if any(s in f for s in glean_subset):
        test_types.add("glean")
        continue

    for test_type, subset in file_subsets.items():
        if any(s in f for s in subset):
            test_types.add(test_type)

if not test_types:
    test_types = {"starfox"}

print(json.dumps(list(test_types)))
