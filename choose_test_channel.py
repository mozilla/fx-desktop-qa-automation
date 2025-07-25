import os
import re
import sys
from subprocess import check_output

ALL_CHANNELS = ["smoke", "l10n"]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SLASH = "/" if "/" in SCRIPT_DIR else "\\"

file_subsets = {
    "smoke": ["modules/data", "modules/page", "modules/browser", "tests/"],
    "l10n": ["l10n_CM/"],
}

l10n_module_patterns = [
    r"modules/page_object_prefs\.py",
    r"modules/data/about_prefs\.components\.json",
    r"modules/page_object_autofill\.py",
    r"modules/data/address_fill\.components\.json",
    r"modules/data/credit_card_fill\.components\.json",
    r"modules/browser_object_autofill_popup\.py",
    r"modules/data/autofill_popup\.components\.json",
]

l10n_module_patterns = set(
    [
        re.compile(val.replace("/", r"\\")) if SLASH == "\\" else re.compile(val)
        for val in l10n_module_patterns
    ]
)

check_output(["git", "fetch", "--quiet", "--depth=1", "origin", "main"])

committed_files = (
    check_output(["git", "--no-pager", "diff", "--name-only", "origin/main"])
    .decode()
    .replace("/", SLASH)
    .splitlines()
)
main_conftest = "conftest.py"
base_page = os.path.join("modules", "page_base.py")

channels = []

if main_conftest in committed_files or base_page in committed_files:
    print(ALL_CHANNELS)
    sys.exit()

for f in committed_files:
    if any([r.match(f) for r in l10n_module_patterns]):
        sys.exit()

    for test_channel in file_subsets:
        for subset in file_subsets[test_channel]:
            print(f, test_channel, subset)
            if subset in f and test_channel not in channels:
                channels.append(test_channel)

if not channels:
    channels = ["smoke"]
print(channels)
