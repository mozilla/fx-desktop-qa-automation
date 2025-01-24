import logging
import os
import re
import subprocess

from modules import taskcluster as tc
from modules import testrail as tr
from modules.testrail import TestRail

FX_PRERC_VERSION_RE = re.compile(r"Mozilla Firefox (\d+)\.(\d\d?)[ab](\d\d?)")
FX_RC_VERSION_RE = re.compile(r"Mozilla Firefox (\d+)\.(\d\d?)")
FX_RELEASE_VERSION_RE = re.compile(r"Mozilla Firefox (\d+)\.(\d\d?)\.(\d\d?)")
TESTRAIL_RUN_FMT = "[{channel} {major}] Automated testing {major}.{minor}b{build}"
PLAN_NAME_RE = re.compile(r"\[(\w+) (\d+)\]")
CONFIG_GROUP_ID = 95
TESTRAIL_FX_DESK_PRJ = 17


def get_plan_title(version_str: str, channel: str) -> str:
    """Given a version string, get the plan_title"""

    version_match = FX_PRERC_VERSION_RE.match(version_str)
    if version_match:
        logging.info(version_match)
        (major, minor, build) = [version_match[n] for n in range(1, 4)]
        logging.info(f"major {major} minor {minor} build {build}")
        plan_title = (
            TESTRAIL_RUN_FMT.replace("{channel}", channel)
            .replace("{major}", major)
            .replace("{minor}", minor)
            .replace("{build}", build)
        )
    else:
        # Version doesn't look like a normal beta, someone updated to the RC
        version_match = FX_RC_VERSION_RE.match(version_str)
        (major, minor) = [version_match[n] for n in range(1, 3)]
        plan_title = (
            TESTRAIL_RUN_FMT.replace("{channel}", channel)
            .replace("{major}", major)
            .replace("{minor}", minor)
            .replace("b{build}", "rc")
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
        return False
    return reportable()


def reportable():
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
    sys_platform = platform.system()
    version = subprocess.check_output(
        [os.environ.get("FX_EXECUTABLE"), "--version"]
    ).decode()
    tr_session = testrail_init()
    first_half, second_half = version.split(".")
    channel = "Beta" if "b" in second_half else "Release"
    if "Nightly" in first_half:
        channel = "Nightly"

    major_version = " ".join(first_half.split(" ")[1:])
    major_number = major_version.split(" ")[-1]
    major_milestone = tr_session.matching_milestone(TESTRAIL_FX_DESK_PRJ, major_version)
    if not major_milestone:
        logging.warning("Reporting: Could not find matching milestone.")
        return False

    channel_milestone = tr_session.matching_submilestone(
        major_milestone, f"{channel} {major_number}"
    )
    if not channel_milestone:
        logging.warning(
            f"Reporting: Could not find matching submilestone for {channel} {major_number}"
        )
        return False

    plan_title = get_plan_title(version, channel)
    this_plan = tr_session.matching_plan_in_milestone(
        TESTRAIL_FX_DESK_PRJ, channel_milestone.get("id"), plan_title
    )
    if not this_plan:
        logging.warning(
            f"Session reportable: could not find {plan_title} (milestone: {channel_milestone.get('id')})"
        )
        return True

    platform = "MacOS" if sys_platform == "Darwin" else sys_platform

    plan_entries = this_plan.get("entries")
    covered_suites = 0
    for entry in plan_entries:
        for run_ in entry.get("runs"):
            if platform in run_.get("config"):
                covered_suites += 1

    num_suites = 0
    for test_dir_name in os.listdir("tests"):
        test_dir = os.path.join("tests", test_dir_name)
        if os.path.isdir(test_dir) and not os.path.exists(
            os.path.join(test_dir, "skip_reporting")
        ):
            num_suites += 1

    logging.warning("Potentially matching run found, may be reportable.")
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
            if key in ["passed", "skipped", "xfailed", "failed"]:
                for run_id in results.get(key):
                    if not output.get(key).get(run_id):
                        output[key][run_id] = results[key][run_id]
                        continue
                    output[key][run_id] += results[key][run_id]
    return output


def mark_results(testrail_session: TestRail, test_results):
    """For each type of result, and per run, mark tests to status in batches"""
    logging.info(f"mark results: object\n{test_results}")
    existing_results = {}
    for category in ["passed", "skipped", "xfailed", "failed"]:
        for run_id in test_results[category]:
            if not existing_results.get(run_id):
                existing_results[run_id] = testrail_session.get_test_results(run_id)
            current_results = {
                result.get("case_id"): result.get("status_id")
                for result in existing_results[run_id]
            }
            suite_id = test_results[category][run_id][0].get("suite_id")
            all_test_cases = [
                result.get("test_case") for result in test_results[category][run_id]
            ]

            # Don't set passed tests to another status.
            test_cases = [tc for tc in all_test_cases if current_results.get(tc) != 1]
            logging.warn(
                f"Setting the following test cases in run {run_id} to {category}: {test_cases}"
            )
            testrail_session.update_test_cases(
                test_results.get("project_id"),
                testrail_run_id=run_id,
                testrail_suite_id=suite_id,
                test_case_ids=test_cases,
                status=category,
            )


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

    for test_case, outcome in results.items():
        logging.info(f"{test_case}: {outcome}")
        if outcome == "rerun":
            logging.info("Rerun result...skipping...")
            continue
        category = next(status for status in passkey if outcome in passkey.get(status))
        if not test_results[category].get(run_id):
            test_results[category][run_id] = []
        test_results[category][run_id].append(
            {"suite_id": suite_id, "test_case": test_case}
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
    channel = os.environ.get("STARFOX_CHANNEL")
    if not channel:
        channel = "Beta"
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
    logging.info(plan_title)
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

    with open(".tmp_testrail_info", "w") as fh:
        fh.write(f"{plan_title}|{config}")

    major_milestone = testrail_session.matching_milestone(
        TESTRAIL_FX_DESK_PRJ, f"Firefox {major}"
    )
    logging.info(f"{channel} {major}")
    channel_milestone = testrail_session.matching_submilestone(
        major_milestone, f"{channel} {major}"
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
    if len(config_matches) >= 1:
        # TODO: change above to == 1
        config_id = config_matches[0].get("id")
        logging.info(f"config id: {config_id}")
    else:
        raise ValueError(f"Should only have one matching TR config: {config}")

    # Find or add suite-based runs on the plan
    # Store test results for later

    last_suite_id = None
    last_description = None
    results_by_suite = {}
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
        logging.info(f"TC: {test_case}: {outcome}")

        if not results_by_suite.get(suite_id):
            results_by_suite[suite_id] = {}
        results_by_suite[suite_id][test_case] = outcome
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
    }

    logging.info(f"n run {last_suite_id}, {last_description}")
    full_test_results = merge_results(
        full_test_results, organize_entries(testrail_session, expected_plan, suite_info)
    )
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
