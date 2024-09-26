import logging
import os
import re
import subprocess

from modules import testrail as tr
from modules.testrail import TestRail

FX_VERSION_RE = re.compile(r"Mozilla Firefox (\d+)\.(\d\d?)b(\d\d?)")
TESTRAIL_RUN_FMT = "[{channel} {major}] Automated testing {major}.{minor}b{build}"
CONFIG_GROUP_ID = 95
TESTRAIL_FX_DESK_PRJ = 17


def testrail_init() -> TestRail:
    # Do TestRail init
    local = os.environ.get("TESTRAIL_BASE_URL").split("/")[2].startswith("127")
    logging.info(f"local = {local}")
    tr_session = tr.TestRail(
        os.environ.get("TESTRAIL_BASE_URL"),
        os.environ.get("TESTRAIL_USERNAME"),
        os.environ.get("TESTRAIL_API_KEY"),
        local,
    )
    return tr_session


def merge_results(*result_sets) -> dict:
    # Merge sets of results
    output = {}
    for results in result_sets:
        logging.info(f"merging {results} into {output}")
        for key in results:
            if not output.get(key):
                output[key] = results[key]
                continue
            if key in ["passed", "failed", "skipped"]:
                for run_id in results.get(key):
                    if not output.get(key).get(run_id):
                        output[key][run_id] = results[key][run_id]
                        continue
                    output[key][run_id] += results[key][run_id]
    logging.info(f"MERGED: {output}")
    return output


def mark_results(testrail_session: TestRail, test_results):
    logging.info(f"mark results: object\n{test_results}")
    existing_results = {}
    for category in ["passed", "failed", "skipped"]:
        for run_id in test_results[category]:
            if not existing_results.get(run_id):
                existing_results[run_id] = testrail_session.get_test_results(run_id)
            current_results = {
                result.get("test_case"): result.get("status_id")
                for result in existing_results[run_id]
            }
            suite_id = test_results[category][run_id][0].get("suite_id")
            all_test_cases = [
                result.get("test_case") for result in test_results[category][run_id]
            ]

            # Don't set passed tests to another status.
            test_cases = [tc for tc in all_test_cases if current_results.get(tc) != 1]
            logging.info(f"==={category}===")
            logging.info(test_cases)
            testrail_session.update_test_cases(
                test_results.get("project_id"),
                testrail_run_id=run_id,
                testrail_suite_id=suite_id,
                test_case_ids=test_cases,
                status=category,
            )


def organize_entries(testrail_session: TestRail, expected_plan: dict, suite_info: dict):
    suite_id = suite_info.get("id")
    suite_description = suite_info.get("description")
    milestone_id = suite_info.get("milestone_id")
    config = suite_info.get("config")
    config_id = suite_info.get("config_id")
    cases_in_suite = suite_info.get("cases")
    results = suite_info.get("results")
    plan_title = expected_plan.get("name")

    logging.info("ORGANIZING")
    logging.info(f"suite: {suite_id} {suite_description} \nplan {plan_title}")
    logging.info(f"config {config_id} {config}")
    logging.info(f"cases: {cases_in_suite}")
    logging.info(results)
    suite_entries = [
        entry
        for entry in expected_plan.get("entries")
        if entry.get("suite_id") == suite_id
    ]

    # Add a missing entry to a plan
    plan_id = expected_plan.get("id")
    if not suite_entries:
        # If no entry, create entry for suite
        for case_id in cases_in_suite:
            logging.info("checking on case {case_id}")
            case = testrail_session.get_test_case(case_id)
            logging.info(f"Test case {case_id} exists in suite {case.get('suite_id')}.")

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
    run_cases = run.get("case_ids")
    if run_cases:
        expected_case_ids = list(set(run_cases + cases_in_suite))
        if len(expected_case_ids) > len(run.get("case_ids")):
            run = testrail_session.update_run_in_entry(
                run.get("id"), case_ids=expected_case_ids
            )

    if run.get("is_completed"):
        logging.info(f"Run {run.get('id')} is already completed.")
        return {}
    run_id = run.get("id")
    passkey = {
        "passed": ["passed", "xpassed", "warnings"],
        "failed": ["failed", "xfailed", "error"],
        "skipped": ["skipped", "deselected"],
    }
    test_results = {
        "project_id": TESTRAIL_FX_DESK_PRJ,
        "passed": {},
        "failed": {},
        "skipped": {},
    }

    for test_case, outcome in results.items():
        logging.info(f"{test_case}: {outcome}")
        if outcome == "rerun":
            logging.info("Rerun result...skipping...")
            continue
        category = next(status for status in passkey if outcome in passkey.get(status))
        logging.info(f"Update run {run_id} - {test_case} - {category}")
        if not test_results[category].get(run_id):
            test_results[category][run_id] = []
        test_results[category][run_id].append(
            {"suite_id": suite_id, "test_case": test_case}
        )

    return test_results


def collect_changes(testrail_session: TestRail, report):
    """doc"""

    # Find milestone to attach to
    version_match = FX_VERSION_RE.match(
        report.get("tests")[0].get("metadata").get("fx_version")
    )
    (major, minor, build) = [version_match[n] for n in range(1, 4)]
    logging.info(f"major {major} minor {minor} build {build}")
    config = report.get("tests")[0].get("metadata").get("machine_config")

    if "linux" in config.lower():
        os_name = "Linux"
        for word in config.split(" "):
            if word.startswith("x"):
                arch = word
        release = subprocess.check_output(["lsb_release", "-d"]).decode()
        release = release.split("\t")[-1].strip()
        release = ".".join(release.split(".")[:-1])
        config = f"{os_name} {release} {arch}"

    major_milestone = testrail_session.matching_milestone(
        TESTRAIL_FX_DESK_PRJ, f"Firefox {major}"
    )
    channel = os.environ.get("STARFOX_CHANNEL")
    if not channel:
        channel = "Beta"
    channel_milestone = testrail_session.matching_submilestone(
        major_milestone, f"{channel} {major}"
    )

    # Find plan to attach runs to, create if doesn't exist
    plan_title = (
        TESTRAIL_RUN_FMT.replace("{channel}", channel)
        .replace("{major}", major)
        .replace("{minor}", minor)
        .replace("{build}", build)
    )
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
    for test in tests:
        (suite_id_str, suite_description) = test.get("metadata").get("suite_id")
        try:
            suite_id = int(suite_id_str.replace("S", ""))
        except (ValueError, TypeError):
            logging.info("No suite number, not reporting...")
            continue
        test_case = test.get("metadata").get("test_case")
        logging.info(f"METADATA: {test.get('metadata')}")
        try:
            int(test_case)
        except (ValueError, TypeError):
            logging.info("No test case number, not reporting...")
            continue

        outcome = test.get("outcome")
        if not results_by_suite.get(suite_id):
            results_by_suite[suite_id] = {}
        results_by_suite[suite_id][test_case] = outcome
        if suite_id != last_suite_id:
            # When we get the last test_case in a suite, add entry, run, results
            if last_suite_id:
                logging.info("n-1 run")
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

                full_test_results = merge_results(
                    full_test_results,
                    organize_entries(testrail_session, expected_plan, suite_info),
                )

        last_suite_id = suite_id
        last_description = suite_description

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
