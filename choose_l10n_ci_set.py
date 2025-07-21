import json
import os
import re
import sys
from collections import defaultdict
from subprocess import check_output

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SLASH = "/" if "/" in SCRIPT_DIR else "\\"
CI_MARK = "@pytest.mark.ci"
HEADED_MARK = "@pytest.mark.headed"
OUTPUT_FILE = "selected_l10n_mappings"


def valid_l10n_mappings():
    mapping = defaultdict(set)
    region_paths = [d for d in os.listdir("./l10n_CM/region/")]
    for region_path in region_paths:
        if region_path != "Unified.json":
            region = region_path.split(".")[0]
            with open(f"./l10n_CM/region/{region_path}", "r+") as f:
                region_file = json.load(f)
                if region_file.get("sites"):
                    for site in region_file.get("sites"):
                        mapping[site].add(region)
    return mapping


def add_selected_mappings(mappings):
    """
    Write the selected mappings to the output file.

    Args:
        mappings (dict): A dictionary of mappings, where the keys are sites and the values are sets of regions.
    """
    for site, regions in mappings.items():
        with open(OUTPUT_FILE, "a+") as f:
            f.write(f"{site} {' '.join(regions)}\n")


def process_changed_file(f, selected_mappings):
    split = f.split(SLASH)
    if f.startswith("l10n_CM/sites/") or f.startswith("l10n_CM/constants/"):
        site = split[2]
        region = split[3]
        region_path = os.path.join("l10n_CM", "region", f"{region}.json")
        if os.path.exists(region_path):
            selected_mappings[site].add(region)
    elif f.startswith("l10n_CM/region/"):
        region = split[-1].split(".")[0]
        for mapping in selected_mappings.values():
            mapping.add(region)


if __name__ == "__main__":
    if os.path.exists(".env"):
        with open(".env") as fh:
            contents = fh.read()
            if "TESTRAIL_REPORT='true'" in contents:
                os.environ["TESTRAIL_REPORT"] = "true"
            if "RUN_ALL='true'" in contents:
                os.environ["MANUAL"] = "true"
    with open(OUTPUT_FILE, "w") as file:
        pass  # File is created or cleared
    l10n_mappings = valid_l10n_mappings()
    if os.environ.get("TESTRAIL_REPORT") or os.environ.get("MANUAL"):
        # Run all tests if this is a scheduled beta or a manual run
        add_selected_mappings(l10n_mappings)
        sys.exit(0)

    re_set_all = [
        r"l10n_CM/Unified/test_.*\.py",
        r"l10n_CM/Unified/conftest\.py",
        r"l10n_CM/conftest\.py",
        r"modules/page_object_prefs\.py",
        r"modules/data/about_prefs\.components\.json",
        r"modules/page_object_autofill\.py",
        r"modules/data/address_fill\.components\.json",
        r"modules/data/credit_card_fill\.components\.json",
        r"modules/browser_object_autofill_popup\.py",
        r"modules/data/autofill_popup\.components\.json",
        r"l10n_CM/run_l10n\.py",
    ]
    re_set_select = [
        r"l10n_CM/constants/.*/.*/.*\.json",
        r"l10n_CM/sites/.*/.*\.json",
        r"l10n_CM/region/.*\.json",
    ]

    re_set_all = set(
        [
            re.compile(val.replace("/", r"\\")) if SLASH == "\\" else re.compile(val)
            for val in re_set_all
        ]
    )
    re_set_select = set(
        [
            re.compile(val.replace("/", r"\\")) if SLASH == "\\" else re.compile(val)
            for val in re_set_select
        ]
    )

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
        # Run all the tests for all mappings if main conftest or basepage changed
        add_selected_mappings(l10n_mappings)
        sys.exit(0)

    # Run all the tests for all mappings if any core l10n model, component, conftest, or tests are changed.
    selected_mappings = defaultdict(set)
    for f in committed_files:
        for re_val in re_set_all:
            if re_val.match(f):
                add_selected_mappings(l10n_mappings)
                sys.exit(0)
        for re_val in re_set_select:
            if re_val.match(f):
                process_changed_file(f, selected_mappings)

    add_selected_mappings(selected_mappings)
    sys.exit(0)
