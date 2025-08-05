import logging
import os
import re
import subprocess
import sys

from choose_l10n_ci_set import distribute_mappings_evenly, valid_l10n_mappings
from modules import taskcluster as tc
from modules import testrail as tr
from modules.testrail import TestRail

FX_PRERC_VERSION_RE = re.compile(r"(\d+)\.(\d\d?)[ab](\d\d?)-build(\d+)")
FX_RC_VERSION_RE = re.compile(r"(\d+)\.(\d\d?)(.*)")
FX_DEVED_VERSION_RE = re.compile(r"(\d+)\.(\d\d?)b(\d\d?)")
FX_RELEASE_VERSION_RE = re.compile(r"(\d+)\.(\d\d?)\.(\d\d?)(.*)")
TESTRAIL_RUN_FMT = (
    "[{channel} {major}] {plan}Automated testing {major}.{minor}b{beta}-build{build}"
)
PLAN_NAME_RE = re.compile(r"\[(\w+) (\d+)\]")
CONFIG_GROUP_ID = 95
TESTRAIL_FX_DESK_PRJ = 17
TC_EXECUTION_TEMPLATE = "https://firefox-ci-tc.services.mozilla.com/tasks/%TASK_ID%/runs/%RUN_ID%/logs/public/logs/live.log"


def get_execution_link() -> str:
    """Using environment variables, get the link to the test execution"""
    link = ""
    if "TASKCLUSTER_PROXY_URL" in os.environ:
        link = TC_EXECUTION_TEMPLATE
        for item in ["RUN_ID", "TASK_ID"]:
            link = link.replace(f"%{item}%", os.environ.get(item))
        return link


def replace_link_in_description(description, os_name) -> str:
    """Add or replace a test execution link in the test run description"""
    logging.warning(f"Modifying plan description for %{os_name}%")
    if os_name not in description:
        # TODO: remove following conditional when links for GHA resolved
        if os_name == "Linux":
            return f"{description}\n[{os_name} execution link]({get_execution_link()})"
    else:
        link = get_execution_link()
        if link in description:
            return description
        lines = description.split("\n")
        for i, line in enumerate(lines):
            if os_name in line:
                lines[i] = (
                    f"{description}\n[{os_name} execution link]({get_execution_link()})"
                )
    return description


def get_plan_title(version_str: str, channel: str) -> str:
    """Given a version string, get the plan_title"""

    version_match = FX_PRERC_VERSION_RE.match(version_str)
    plan_prefix = "L10N " if os.environ.get("FX_L10N") else ""
    if channel == "Devedition":
        logging.info(f"DevEdition: {version_str}")
        version_match = FX_DEVED_VERSION_RE.match(version_str)
        (major, minor, beta) = [version_match[n] for n in range(1, 4)]
        plan_title = (
            TESTRAIL_RUN_FMT.replace("{channel}", channel)
            .replace("{major}", major)
            .replace("{plan}", plan_prefix)
            .replace("{minor}", minor)
            .replace("{beta}", beta)
            .split("-")[0]
        )
    elif version_match:
        logging.info(version_match)
        (major, minor, beta, build) = [version_match[n] for n in range(1, 5)]
        logging.info(f"major {major} minor {minor} beta {beta} build {build}")
        plan_title = (
            TESTRAIL_RUN_FMT.replace("{channel}", channel)
            .replace("{major}", major)
            .replace("{plan}", plan_prefix)
            .replace("{minor}", minor)
            .replace("{beta}", beta)
            .replace("{build}", build)
        )
    else:
        # Version doesn't look like a normal beta, someone updated to the RC
        version_match = FX_RC_VERSION_RE.match(version_str)
        (major, minor) = [version_match[n] for n in range(1, 3)]
        plan_title = (
            TESTRAIL_RUN_FMT.replace("{channel}", channel)
            .replace("{plan}", plan_prefix)
            .replace("{major}", major)
            .replace("{minor}", minor)
            .replace("{beta}", "rc")
        )
    return plan_title


def tc_reportable():
    """For CI: return True if run is reportable, but get TC creds first"""
    creds = tc.get_tc_secret()
    if creds:
        os.environ["TESTRAIL_USERNAME"] = creds.get("TESTRAIL_USERNAME")
        os.environ["TESTRAIL_API_KEY"] = creds.get("TESTRAIL_API_KEY")
        os.environ["TESTRAIL_BASE_URL"] = creds.get("TESTRAIL_BASE_URL")
    else:
        sys.exit(100)

    if reportable():
        sys.exit(0)
    else:
        sys.exit(100)


def reportable(platform_to_test=None):
    """Return true if we should report to TestRail"""
    import platform

    if not os.environ.get("TESTRAIL_REPORT"):
        logging.warning("TESTRAIL_REPORT not set, session not reportable.")
        return False

    # If we ask for reporting, we can force a report
    if os.environ.get("REPORTABLE"):
        logging.warning("REPORTABLE=true; we will report this session.")
        return True

    # Find the correct test plan
    sys_platform = platform_to_test or platform.system()
    if platform_to_test:
        os.environ["FX_PLATFORM"] = platform_to_test
    version = (
        subprocess.check_output([sys.executable, "./collect_executables.py", "-n"])
        .strip()
        .decode()
    )
    logging.warning(f"Got version from collect_executable.py! {version}")
    tr_session = testrail_init()
    major_number, second_half = version.split(".")
    if "-" in second_half:
        minor_num, _ = second_half.split("-")
    else:
        minor_num = second_half
    channel = os.environ.get("FX_CHANNEL") or "beta"
    channel = channel.title()
    if not channel:
        if "b" in minor_num:
            channel = "Beta"
        else:
            channel = "Release"

    major_version = f"Firefox {major_number}"
    major_milestone = tr_session.matching_milestone(TESTRAIL_FX_DESK_PRJ, major_version)
    if not major_milestone:
        logging.warning(
            f"Not reporting: Could not find matching milestone: Firefox {major_version}"
        )
        return False

    channel_milestone = tr_session.matching_submilestone(
        major_milestone, f"{channel} {major_number}"
    )
    if not channel_milestone:
        if channel == "Devedition":
            channel_milestone = tr_session.matching_submilestone(
                major_milestone, f"Beta {major_number}"
            )
        if not channel_milestone:
            logging.warning(
                f"Not reporting: Could not find matching submilestone for {channel} {major_number}"
            )
            return False

    plan_title = get_plan_title(version, channel)
    logging.warning(f"Plan title: {plan_title}")
    this_plan = tr_session.matching_plan_in_milestone(
        TESTRAIL_FX_DESK_PRJ, channel_milestone.get("id"), plan_title
    )
    if not this_plan:
        logging.warning(
            f"Session reportable: could not find {plan_title} (milestone: {channel_milestone.get('id')})"
        )
        return True

    if platform_to_test:
        sys_platform = platform_to_test
    platform = "MacOS" if sys_platform == "Darwin" else sys_platform

    plan_entries = this_plan.get("entries")
    if os.environ.get("FX_L10N"):
        report = True
        beta_version = int(minor_num.split("b")[-1])
        distributed_mappings = distribute_mappings_evenly(
            valid_l10n_mappings(), beta_version
        )
        covered_mappings = 0
        # keeping this logic to still see how many mappings are reported.
        for entry in plan_entries:
            if entry.get("name") in distributed_mappings:
                report = False
                site = entry.get("name")
                for run_ in entry.get("runs"):
                    if run_.get("config"):
                        run_region, run_platform = run_.get("config").split("-")
                        covered_mappings += (
                            1
                            if run_region in distributed_mappings[site]
                            and platform in run_platform
                            else 0
                        )
        logging.warning(
            f"Potentially matching run found for {platform}, may be reportable. (Found {covered_mappings} site/region mappings reported.)"
        )
        # Only report when there is a new beta and no other site/region mappings are reported.
        return report or covered_mappings == 0
    else:
        covered_suites = 0
        for entry in plan_entries:
            for run_ in entry.get("runs"):
                if run_.get("config") and platform in run_.get("config"):
                    covered_suites += 1

        num_suites = 0
        for test_dir_name in os.listdir("tests"):
            test_dir = os.path.join("tests", test_dir_name)
            if os.path.isdir(test_dir) and not os.path.exists(
                os.path.join(test_dir, "skip_reporting")
            ):
                num_suites += 1

        logging.warning(
            f"Potentially matching run found for {platform}, may be reportable. ({covered_suites} out of {num_suites} suites already reported.)"
        )
        return covered_suites < num_suites


def testrail_init() -> TestRail:
    """Connect to a TestRail API session"""
    local = os.environ.get("TESTRAIL_BASE_URL").split("/")[2].startswith("127")
    tr_session = tr.TestRail(
        os.environ.get("TESTRAIL_BASE_URL"),
        os.environ.get("TESTRAIL_USERNAME"),
        os.environ.get("TESTRAIL_API_KEY"),
        local,
    )
    return tr_session


def merge_results(*result_sets) -> dict:
    """Merge dictionaries of test results"""
    output = {}
    for results in result_sets:
        for key in results:
            if not output.get(key):
                output[key] = results[key]
                continue
            if key in ["passed", "skipped", "blocked", "xfailed", "failed"]:
                for run_id in results.get(key):
                    if not output.get(key).get(run_id):
                        output[key][run_id] = results[key][run_id]
                        continue
                    output[key][run_id] += results[key][run_id]
    return output


def mark_results(testrail_session: TestRail, test_results):
    """For each type of result, and per run, mark tests to status in batches"""
    logging.warning(f"mark results: object\n{test_results}")
    existing_results = {}
    # don't send update requests for skipped test cases
    for category in ["passed", "blocked", "xfailed", "failed"]:
        # Skip the category if it doesn't exist
        if test_results.get(category) is None:
            logging.warning(f"{category} does not exist for this test run")
            continue
        for run_id in test_results[category]:
            if not existing_results.get(run_id):
                existing_results[run_id] = testrail_session.get_test_results(run_id)
            current_results = {
                result.get("case_id"): result.get("status_id")
                for result in existing_results[run_id]
            }
            suite_id = test_results[category][run_id][0].get("suite_id")

            all_test_cases = []
            all_durations = []
            for result in test_results[category][run_id]:
                all_test_cases.append(result.get("test_case"))
                all_durations.append(result.get("duration"))

            # Don't set passed tests to another status.
            test_cases_ids = []
            durations = []
            for i, test_case in enumerate(all_test_cases):
                if current_results.get(test_case) != 1:
                    test_cases_ids.append(test_case)
                    durations.append(all_durations[i])
            logging.warning(
                f"Setting the following test cases in run {run_id} to {category}: {test_cases_ids}"
            )
            logging.warning(
                f"Setting the following test cases {test_cases_ids} to duration {durations}"
            )
            testrail_session.update_test_cases(
                test_results.get("project_id"),
                testrail_run_id=run_id,
                testrail_suite_id=suite_id,
                test_case_ids=test_cases_ids,
                status=category,
                elapsed=durations,
            )


def organize_l10n_entries(
    testrail_session: TestRail, expected_plan: dict, suite_info: dict
):
    # suite and milestone info
    suite_id = suite_info.get("id")
    milestone_id = suite_info.get("milestone_id")

    # Config
    config = suite_info.get("config")
    site = os.environ.get("CM_SITE")
    config_id = suite_info.get("config_id")

    # Cases and results
    cases_in_suite = suite_info.get("cases")
    cases_in_suite = [int(n) for n in cases_in_suite]
    results = suite_info.get("results")
    durations = suite_info.get("durations")
    plan_title = expected_plan.get("name")

    site_entries = [
        entry for entry in expected_plan.get("entries") if entry.get("name") == site
    ]

    # Add a missing entry to a plan
    plan_id = expected_plan.get("id")
    if not site_entries:
        # If no entry, create entry for site
        logging.info(f"Create entry in plan {plan_id} for site {site}")
        logging.info(f"cases: {cases_in_suite}")
        entry = testrail_session.create_new_plan_entry(
            plan_id=plan_id,
            suite_id=suite_id,
            name=site,
            description="Automation-generated test plan entry",
            case_ids=cases_in_suite,
        )

        expected_plan = testrail_session.matching_plan_in_milestone(
            TESTRAIL_FX_DESK_PRJ, milestone_id, plan_title
        )
        site_entries = [
            entry for entry in expected_plan.get("entries") if entry.get("name") == site
        ]

    if len(site_entries) != 1:
        logging.info("Suite entries are broken somehow")

    # There should only be one entry per site per plan
    # Check that this entry has a run with the correct config
    # And if not, make that run
    entry = site_entries[0]
    config_runs = [run for run in entry.get("runs") if run.get("config") == config]

    logging.info(f"config runs {config_runs}")
    if not config_runs:
        expected_plan = testrail_session.create_test_run_on_plan_entry(
            plan_id,
            entry.get("id"),
            [config_id],
            description=f"Auto test plan entry for site: {site}",
            case_ids=cases_in_suite,
        )
        site_entries = [
            entry for entry in expected_plan.get("entries") if entry.get("name") == site
        ]
        entry = site_entries[0]
        logging.info(f"new entry: {entry}")
        config_runs = [run for run in entry.get("runs") if run.get("config") == config]
    run = testrail_session.get_run(config_runs[0].get("id"))

    # If the run is missing cases, add them
    run_cases = [
        t.get("case_id") for t in testrail_session.get_test_results(run.get("id"))
    ]
    if run_cases:
        expected_case_ids = list(set(run_cases + cases_in_suite))
        if len(expected_case_ids) > len(run_cases):
            testrail_session.update_run_in_entry(
                run.get("id"), case_ids=expected_case_ids, include_all=False
            )
            run = testrail_session.get_run(config_runs[0].get("id"))
            run_cases = [
                t.get("case_id")
                for t in testrail_session.get_test_results(run.get("id"))
            ]

    if run.get("is_completed"):
        logging.info(f"Run {run.get('id')} is already completed.")
        return {}
    run_id = run.get("id")

    # Gather the test results by category of result
    passkey = {
        "passed": ["passed", "xpassed", "warnings"],
        "failed": ["failed", "error"],
        "xfailed": ["xfailed"],
        "blocked": ["skipped", "deselected"],
    }
    test_results = {
        "project_id": TESTRAIL_FX_DESK_PRJ,
        "passed": {},
        "failed": {},
        "xfailed": {},
        "skipped": {},  # need to remove and replace with blocked
        "blocked": {},
    }

    for test_case in results.keys():
        outcome = results[test_case]
        duration = durations[test_case]
        logging.info(f"{test_case}: {outcome} {duration}")
        if outcome == "rerun":
            logging.info("Rerun result...skipping...")
            continue
        category = next(status for status in passkey if outcome in passkey.get(status))
        if not test_results[category].get(run_id):
            test_results[category][run_id] = []
        test_results[category][run_id].append(
            {
                "suite_id": suite_id,
                "site": site,
                "test_case": test_case,
                "duration": f"{duration}s",
            }
        )

    return test_results


def organize_entries(testrail_session: TestRail, expected_plan: dict, suite_info: dict):
    """
    When we get to the level of entries on a TestRail plan, we need to make sure:
     * the entry exists or is created
     * a run matching the current config / platform exists or is created
     * the test cases we care about are on that run or are added
     * test results are batched by run and result type (passed, skipped, failed)
    """

    # Suite and milestone info
    suite_id = suite_info.get("id")
    suite_description = suite_info.get("description")
    milestone_id = suite_info.get("milestone_id")

    # Config
    config = suite_info.get("config")
    config_id = suite_info.get("config_id")

    # Cases and results
    cases_in_suite = suite_info.get("cases")
    cases_in_suite = [int(n) for n in cases_in_suite]
    results = suite_info.get("results")
    durations = suite_info.get("durations")
    plan_title = expected_plan.get("name")

    suite_entries = [
        entry
        for entry in expected_plan.get("entries")
        if entry.get("suite_id") == suite_id
    ]

    # Add a missing entry to a plan
    plan_id = expected_plan.get("id")
    if not suite_entries:
        # If no entry, create entry for suite
        logging.info(f"Create entry in plan {plan_id} for suite {suite_id}")
        logging.info(f"cases: {cases_in_suite}")
        entry = testrail_session.create_new_plan_entry(
            plan_id=plan_id,
            suite_id=suite_id,
            name=suite_description,
            description="Automation-generated test plan entry",
            case_ids=cases_in_suite,
        )

        expected_plan = testrail_session.matching_plan_in_milestone(
            TESTRAIL_FX_DESK_PRJ, milestone_id, plan_title
        )
        suite_entries = [
            entry
            for entry in expected_plan.get("entries")
            if entry.get("suite_id") == suite_id
        ]

    if len(suite_entries) != 1:
        logging.info("Suite entries are broken somehow")

    # There should only be one entry per suite per plan
    # Check that this entry has a run with the correct config
    # And if not, make that run
    entry = suite_entries[0]
    config_runs = [run for run in entry.get("runs") if run.get("config") == config]

    logging.info(f"config runs {config_runs}")
    if not config_runs:
        expected_plan = testrail_session.create_test_run_on_plan_entry(
            plan_id,
            entry.get("id"),
            [config_id],
            description=f"Auto test plan entry: {suite_description}",
            case_ids=cases_in_suite,
        )
        suite_entries = [
            entry
            for entry in expected_plan.get("entries")
            if entry.get("suite_id") == suite_id
        ]
        entry = suite_entries[0]
        logging.info(f"new entry: {entry}")
        config_runs = [run for run in entry.get("runs") if run.get("config") == config]
    run = testrail_session.get_run(config_runs[0].get("id"))

    # If the run is missing cases, add them
    run_cases = [
        t.get("case_id") for t in testrail_session.get_test_results(run.get("id"))
    ]
    if run_cases:
        expected_case_ids = list(set(run_cases + cases_in_suite))
        if len(expected_case_ids) > len(run_cases):
            testrail_session.update_run_in_entry(
                run.get("id"), case_ids=expected_case_ids, include_all=False
            )
            run = testrail_session.get_run(config_runs[0].get("id"))
            run_cases = [
                t.get("case_id")
                for t in testrail_session.get_test_results(run.get("id"))
            ]

    if run.get("is_completed"):
        logging.info(f"Run {run.get('id')} is already completed.")
        return {}
    run_id = run.get("id")

    # Gather the test results by category of result
    passkey = {
        "passed": ["passed", "xpassed", "warnings"],
        "failed": ["failed", "error"],
        "xfailed": ["xfailed"],
        "skipped": ["skipped", "deselected"],
    }
    test_results = {
        "project_id": TESTRAIL_FX_DESK_PRJ,
        "passed": {},
        "failed": {},
        "xfailed": {},
        "skipped": {},
    }

    for test_case in results.keys():
        outcome = results[test_case]
        duration = durations[test_case]
        logging.info(f"{test_case}: {outcome} {duration}")
        if outcome == "rerun":
            logging.info("Rerun result...skipping...")
            continue
        category = next(status for status in passkey if outcome in passkey.get(status))
        if not test_results[category].get(run_id):
            test_results[category][run_id] = []
        test_results[category][run_id].append(
            {"suite_id": suite_id, "test_case": test_case, "duration": f"{duration}s"}
        )

    return test_results


def collect_changes(testrail_session: TestRail, report):
    """
    Determine what structure needs to be built so that we can report TestRail results.
     * Construct config and plan name
     * Find the right milestone to report to
     * Find the right submilestone
     * Find the right plan to report to, or create it
     * Find the right config to attach to the run, or create it
     * Use organize_entries to create the rest of the structure and gather results
     * Use mark_results to update the test runs
    """

    # Find milestone to attach to
    channel = os.environ.get("FX_CHANNEL") or "beta"
    channel = channel.title()
    if channel == "Release":
        raise ValueError("Release reporting currently not supported")

    metadata = None
    for test in report.get("tests"):
        if test.get("metadata"):
            metadata = test.get("metadata")
            break

    if not metadata:
        logging.error("No metadata collected. Exiting without report.")
        return False

    version_str = metadata.get("fx_version")
    plan_title = get_plan_title(version_str, channel)
    logging.warning(
        f"Got plan title: {plan_title} from version {version_str} and channel {channel}"
    )
    plan_match = PLAN_NAME_RE.match(plan_title)
    (_, major) = [plan_match[n] for n in range(1, 3)]
    config = metadata.get("machine_config")

    if "linux" in config.lower():
        os_name = "Linux"
        for word in config.split(" "):
            if word.startswith("x"):
                arch = word
        release = subprocess.check_output(["lsb_release", "-d"]).decode()
        release = release.split("\t")[-1].strip()
        release = ".".join(release.split(".")[:-1])
        config = f"{os_name} {release} {arch}"

    if os.environ.get("FX_L10N") and os.environ.get("FX_REGION"):
        config = f"{os.environ.get('FX_REGION')}-{config}"

    logging.warning(f"Reporting for config: {config}")
    if not config.strip():
        raise ValueError("Config cannot be blank.")

    with open(".tmp_testrail_info", "w") as fh:
        fh.write(f"{plan_title}|{config}")

    major_milestone = testrail_session.matching_milestone(
        TESTRAIL_FX_DESK_PRJ, f"Firefox {major}"
    )
    logging.info(f"{channel} {major}")
    channel_milestone = testrail_session.matching_submilestone(
        major_milestone, f"{channel} {major}"
    )
    if (not channel_milestone) and channel == "Devedition":
        channel_milestone = testrail_session.matching_submilestone(
            major_milestone, f"Beta {major}"
        )

    # Find plan to attach runs to, create if doesn't exist
    logging.info(f"Plan title: {plan_title}")
    milestone_id = channel_milestone.get("id")
    expected_plan = testrail_session.matching_plan_in_milestone(
        TESTRAIL_FX_DESK_PRJ, milestone_id, plan_title
    )
    if expected_plan is None:
        logging.info(f"Create plan '{plan_title}' in milestone {milestone_id}")
        expected_plan = testrail_session.create_new_plan(
            TESTRAIL_FX_DESK_PRJ,
            plan_title,
            description="Automation-generated test plan",
            milestone_id=milestone_id,
        )
    elif expected_plan.get("is_completed"):
        logging.info(f"Plan found ({expected_plan.get('id')}) but is completed.")
        return None

    # Add execution link to plan description

    os_name = config.split(" ")[0]
    description = replace_link_in_description(expected_plan["description"], os_name)
    testrail_session.update_plan(expected_plan["id"], description=description)

    # Find or add correct config for session

    config_matches = None
    tried = False
    while not config_matches:
        config_matches = testrail_session.matching_configs(
            TESTRAIL_FX_DESK_PRJ, CONFIG_GROUP_ID, config
        )
        if tried:
            break
        if not config_matches:
            logging.info("Creating config...")
            testrail_session.add_config(CONFIG_GROUP_ID, config)
        tried = True
    if len(config_matches) == 1:
        config_id = config_matches[0].get("id")
        logging.info(f"config id: {config_id}")
    else:
        raise ValueError(f"Should only have one matching TR config: {config}")

    # Find or add suite-based runs on the plan
    # Store test results for later

    last_suite_id = None
    last_description = None
    results_by_suite = {}
    durations_by_suite = {}
    full_test_results = {}
    tests = [
        test
        for test in report.get("tests")
        if "metadata" in test and "suite_id" in test.get("metadata")
    ]
    tests = sorted(tests, key=lambda item: item.get("metadata").get("suite_id"))

    # Iterate through the tests; when we finish a line of same-suite tests, gather them
    for test in tests:
        (suite_id_str, suite_description) = test.get("metadata").get("suite_id")
        try:
            suite_id = int(suite_id_str.replace("S", ""))
        except (ValueError, TypeError):
            logging.info("No suite number, not reporting...")
            continue
        test_case = test.get("metadata").get("test_case")
        try:
            int(test_case)
        except (ValueError, TypeError):
            logging.info("No test case number, not reporting...")
            continue

        outcome = test.get("outcome")
        # Tests reported as rerun are a problem -- we need to know pass/fail
        if outcome == "rerun":
            outcome = test.get("call").get("outcome")
        duration = (
            test["setup"]["duration"]
            + test["call"]["duration"]
            + test["teardown"]["duration"]
        )
        logging.info(f"TC: {test_case}: {outcome} using {duration}s ")

        if not results_by_suite.get(suite_id):
            results_by_suite[suite_id] = {}
            durations_by_suite[suite_id] = {}
        results_by_suite[suite_id][test_case] = outcome
        durations_by_suite[suite_id].setdefault(test_case, 0)
        durations_by_suite[suite_id][test_case] = round(
            durations_by_suite[suite_id][test_case] + duration, 2
        )

        if suite_id != last_suite_id:
            # When we get the last test_case in a suite, add entry, run, results
            if last_suite_id:
                logging.info("n-1 run")
                cases_in_suite = list(results_by_suite[last_suite_id].keys())
                cases_in_suite = [int(n) for n in cases_in_suite]
                suite_info = {
                    "id": last_suite_id,
                    "description": last_description,
                    "milestone_id": milestone_id,
                    "config": config,
                    "config_id": config_id,
                    "cases": cases_in_suite,
                    "results": results_by_suite[last_suite_id],
                    "durations": durations_by_suite[last_suite_id],
                }

                full_test_results = merge_results(
                    full_test_results,
                    organize_entries(testrail_session, expected_plan, suite_info),
                )

        last_suite_id = suite_id
        last_description = suite_description

    # We do need to run this again because we will always have one last suite.
    cases_in_suite = list(results_by_suite[last_suite_id].keys())
    suite_info = {
        "id": last_suite_id,
        "description": last_description,
        "milestone_id": milestone_id,
        "config": config,
        "config_id": config_id,
        "cases": cases_in_suite,
        "results": results_by_suite[last_suite_id],
        "durations": durations_by_suite[last_suite_id],
    }

    logging.info(f"n run {last_suite_id}, {last_description}")
    if os.environ.get("FX_L10N"):
        entries = organize_l10n_entries(testrail_session, expected_plan, suite_info)
        return merge_results(
            full_test_results,
            entries,
        )
    full_test_results = merge_results(
        full_test_results, organize_entries(testrail_session, expected_plan, suite_info)
    )
    logging.warning(f"full test results: {full_test_results}")

    return full_test_results


def update_all_test_cases(testrail_session, field_to_update, field_content):
    """
    Sets the field of every test case to the new content
    """
    print(f"updating all test cases to have {field_content} in {field_to_update}")
    test_suites = [d for d in os.listdir("./tests/")]
    for test_suite in test_suites:
        for test in os.listdir(f"./tests/{test_suite}"):
            if test[0:4] != "test":
                continue
            # Find tests and parse test case number
            file_name = f"tests/{test_suite}/{test}"
            with open(file_name) as f:
                for line in f:
                    if line.startswith("def test_case():"):
                        break
                line = f.readline().strip()
                ind = line.find('"') + 1
                test_case = line[ind:-1]
                if test_case in ("", "N/A"):
                    continue
                # Update the test case
                print(f"updating {test_case}: {file_name}")
                testrail_session.update_case_field(
                    test_case, field_to_update, field_content
                )
