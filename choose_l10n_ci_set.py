import json
import logging
import os
import re
import subprocess
import sys
from collections import defaultdict
from subprocess import check_output

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SLASH = "/" if "/" in SCRIPT_DIR else "\\"
CI_MARK = "@pytest.mark.ci"
HEADED_MARK = "@pytest.mark.headed"
OUTPUT_FILE = "selected_l10n_mappings"


def valid_l10n_mappings():
    """
    Get a dictionary of valid l10n mappings by going through the region files.

    Returns:
        The dictionary of valid l10n mappings.
    """
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


def distribute_mappings_evenly(mappings, version):
    """
    Distribute the selected mappings if its a reportable run.

    Args:
        mappings (dict): A dictionary of mappings, where the keys are sites and the values are sets of regions.
        version (int): The beta_version of the beta.
    """
    if not mappings:
        return {}
    if os.environ.get("TESTRAIL_REPORT"):
        # sort the mappings by the length of the regions per site
        mappings = dict(
            sorted(mappings.items(), key=lambda val: len(val[1]), reverse=True)
        )
        # place the mappings into 3 containers evenly according to the load
        loads = [0, 0, 0]
        containers = [defaultdict(set) for _ in range(3)]
        for key, value in mappings.items():
            min_idx = loads.index(min(loads))
            containers[min_idx][key] = value
            loads[min_idx] += len(value)
        # get container index according to beta beta_version
        run_idx = version % 3
        return containers[run_idx]
    else:
        return mappings


def process_changed_file(f, selected_mappings):
    """
    process the changed file to add the site/region mappings.

    Args:
        f: the changed file.
        selected_mappings: the selected mappings dictionary (updated in place).
    """
    split = f.split(SLASH)
    if f.startswith(os.path.join("l10n_CM", "sites")) or f.startswith(
        os.path.join("l10n_CM", "constants")
    ):
        # if constants or sites are changed, add a single site/region mapping entry.
        site = split[2]
        region = split[3]
        region_path = os.path.join("l10n_CM", "region", f"{region}.json")
        # make sure the region mapping file exists before adding the mapping
        if os.path.exists(region_path):
            selected_mappings[site].add(region)
    elif f.startswith(os.path.join("l10n_CM", "region")):
        # if a region file is changed, add the region to each site mapping.
        region = split[-1].split(".")[0]
        with open(f, "r+") as f:
            region_file = json.load(f)
            for site in region_file.get("sites", []):
                selected_mappings[site].add(region)


def save_mappings(selected_container):
    """
    Save the selected mappings to the output file.

        Args:
            selected_container: the selected mappings container.
    """
    if not selected_container:
        return
    current_running_mappings = [
        f"{key} {' '.join(value)}\n" for key, value in selected_container.items()
    ]
    logging.warning(f"Running the mappings:\n{''.join(current_running_mappings)}")
    with open(OUTPUT_FILE, "a+") as f:
        f.writelines(current_running_mappings)


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
    try:
        beta_version = int(
            (
                subprocess.check_output(
                    [sys.executable, "./collect_executables.py", "-n"]
                )
                .strip()
                .decode()
            )
            .split("-")[0]
            .split(".")[1]
            .split("b")[1]
        )
    except ValueError:
        # failsafe beta_version
        beta_version = 0
    l10n_mappings = valid_l10n_mappings()
    sample_mappings = {k: v for k, v in l10n_mappings.items() if k.startswith("demo")}
    if os.environ.get("TESTRAIL_REPORT") or os.environ.get("MANUAL"):
        # Run all tests if this is a scheduled beta or a manual run
        save_mappings(distribute_mappings_evenly(l10n_mappings, beta_version))
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
    ]
    re_set_select = [
        r"l10n_CM/constants/.*/.*/.*\.json",
        r"l10n_CM/sites/.*/.*/.*\.html",
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
    selected_mappings = defaultdict(set)
    if main_conftest in committed_files or base_page in committed_files:
        # Run sample tests for all mappings if main conftest or basepage changed
        selected_mappings |= sample_mappings

    # Run sample tests for all mappings if any core l10n model, component, conftest, or tests are changed.
    for f in committed_files:
        # check if constants, sites or region directory files were changed or added.
        # if so, add the site/region mappings.
        for re_val in re_set_select:
            if re_val.match(f):
                process_changed_file(f, selected_mappings)
        for re_val in re_set_all:
            if re_val.match(f):
                selected_mappings |= sample_mappings
                break

    save_mappings(distribute_mappings_evenly(selected_mappings, beta_version))
    sys.exit(0)
