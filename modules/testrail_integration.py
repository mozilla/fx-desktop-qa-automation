import logging
import os
import re

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


def execute_changes(testrail_session: TestRail, changelist):
    """Doc"""
    # Check if config exists, if not create it
    config_matches = None
    tried = False
    logging.info("Change dump---")
    logging.info(changelist)
    while not config_matches:
        config_matches = testrail_session.matching_configs(
            TESTRAIL_FX_DESK_PRJ, CONFIG_GROUP_ID, changelist.get("config")
        )
        if tried:
            break
        if not config_matches:
            testrail_session.add_config(CONFIG_GROUP_ID, changelist.get("config"))
        tried = True
    if len(config_matches) >= 1:
        config_id = config_matches[0].get("id")
    else:
        raise ValueError(
            f"Should only have one matching TR config: {changelist.get('config')}"
        )
    for suite_id in changelist.get("changes"):
        change = changelist["changes"][suite_id]
        logging.info(f"  - PLANNED CHANGE: {change}")
        plan_id = change.get("plan_id")
        suite_description = change.get("name")

        if change.get("change_type") == "create":
            entry = testrail_session.create_new_plan_entry(
                plan_id=plan_id,
                suite_id=suite_id,
                name=suite_description,
                description="Automation-generated test plan entry",
                case_ids=change.get("case_ids"),
            )
        else:
            entry = change.get("entry")
        if change.get("change_type") in ["create", "update_add_runs"]:
            testrail_session.create_test_run_on_plan_entry(
                plan_id,
                entry.get("id"),
                [config_id],
                description=f"Auto test plan entry: {suite_description}",
                case_ids=change.get("case_ids"),
            )


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
            testrail_session.update_test_cases(
                test_results.get("project_id"),
                testrail_run_id=run_id,
                testrail_suite_id=suite_id,
                test_case_ids=test_cases,
                status=category,
            )


def collect_changes(testrail_session: TestRail, report):
    version_match = FX_VERSION_RE.match(
        report.get("tests")[0].get("metadata").get("fx_version")
    )
    (major, minor, build) = [version_match[n] for n in range(1, 4)]
    logging.info(f"major {major} minor {minor} build {build}")
    config = report.get("tests")[0].get("metadata").get("machine_config")

    major_milestone = testrail_session.matching_milestone(
        TESTRAIL_FX_DESK_PRJ, f"Firefox {major}"
    )
    channel = os.environ.get("STARFOX_CHANNEL")
    if not channel:
        channel = "Beta"
    channel_milestone = testrail_session.matching_submilestone(
        major_milestone, f"{channel} {major}"
    )
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
        new_plan = True
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
    else:
        new_plan = False

    entry_changes = {"config": config, "changes": {}}
    test_results = {
        "project_id": TESTRAIL_FX_DESK_PRJ,
        "passed": {},
        "failed": {},
        "skipped": {},
    }
    create_suite = False
    for test in report.get("tests"):
        (suite_id_str, suite_description) = test.get("metadata").get("suite_id")
        suite_id = int(suite_id_str.replace("S", ""))
        test_case = test.get("metadata").get("test_case")
        logging.info(f"METADATA: {test.get('metadata')}")
        try:
            int(test_case)
        except ValueError:
            continue
        # config = test.get("metadata").get("machine_config")
        outcome = test.get("outcome")

        suite_entries = [
            entry
            for entry in expected_plan.get("entries")
            if entry.get("suite_id") == suite_id
        ]
        if not suite_entries and not create_suite:
            # If no entry, create entry for suite and platform
            plan_id = expected_plan.get("id")
            logging.info(f"Create entry in plan {plan_id} for suite {suite_id}")
            entry_changes["changes"][suite_id] = {
                "plan_id": plan_id,
                "change_type": "create",
                "name": suite_description,
                "case_ids": [int(test_case)],
            }
            create_suite = True

            # expected_plan["entries"].append(
            # )
        elif not suite_entries and create_suite:
            entry_changes["changes"][suite_id]["case_ids"].append(int(test_case))
        else:
            for entry in suite_entries:
                logging.info(
                    f"For entry {entry['name']}, update if case_ids does not contain {test_case}"
                )
                logging.info(f"If runs list is empty, add placeholder.")
                logging.info(f"FULL CHANGELIST ## {entry_changes}")
                logging.info(f"FULL SUITE ENTRY~~ {entry}")
                if not entry_changes.get("changes").get(suite_id):
                    logging.info("Door 1")
                    entry_changes["changes"][suite_id] = {"entry": entry}
                if not entry.get("runs"):
                    if not entry_changes["changes"][suite_id].get("change_type"):
                        logging.info("Door 2")
                        entry_changes["changes"][suite_id]["change_type"] = (
                            "update_add_runs"
                        )
                    if entry_changes["changes"][suite_id].get("case_ids"):
                        logging.info("Door 3")
                        entry_changes["changes"][suite_id]["case_ids"].append(
                            int(test_case)
                        )
                    else:
                        logging.info("Won a goat")
                        entry_changes["changes"][suite_id]["case_ids"] = [
                            int(test_case)
                        ]

                # If you're here, you have runs in your entry
                config_runs = [
                    run for run in entry.get("runs") if run.get("config") == config
                ]
                logging.info(f"config runs {config_runs}")
                if not config_runs:
                    if entry_changes["changes"][suite_id].get("case_ids"):
                        entry_changes["changes"][suite_id]["case_ids"].append(
                            int(test_case)
                        )
                    else:
                        entry_changes["changes"][suite_id]["case_ids"] = [
                            int(test_case)
                        ]
                elif len(config_runs) > 1:
                    # Throw an error; we should only have one run per config per entry in plan
                    pass
                else:
                    # Config run has one match, check if all cases exist
                    pass

                run = config_runs[0]
                if run.get("is_completed"):
                    logging.info(f"Run {run.get('id')} is already completed.")
                    continue
                run_id = run.get("id")
                passkey = {
                    "passed": ["passed", "xpassed", "warnings"],
                    "failed": ["failed", "xfailed", "error"],
                    "skipped": ["skipped", "deselected"],
                }
                category = next(
                    status for status in passkey if outcome in passkey.get(status)
                )
                logging.info(f"Update run {run_id} - {test_case} - {category}")
                if not test_results[category].get(run_id):
                    test_results[category][run_id] = []
                test_results[category][run_id].append(
                    {"suite_id": suite_id, "test_case": test_case}
                )
    return (entry_changes, test_results)
