from modules import testrail as tr
from modules.testrail import TestRail

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
    while not config_matches:
        config_matches = testrail_session.matching_configs(
            TESTRAIL_FX_DESK_PRJ, CONFIG_GROUP_ID, changelist.get("config")
        )
        if tried:
            break
        if not config_matches:
            testrail_session.add_config(CONFIG_GROUP_ID, changelist.get("config"))
        tried = True
    if len(config_matches) == 1:
        config_id = config_matches[0].get("id")
    else:
        raise ValueError(
            f"Should only have one matching TR config: {changelist.get('config')}"
        )
    for suite_id in changelist:
        change = changelist[suite_id]
        plan_id = change.get("plan_id")

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
                [change.get("config")],
                description=f"Auto test plan entry: {suite_description}",
                case_ids=[change.get("cases_to_add_to_run")],
            )


def mark_passes(testrail_session: TestRail, test_results):
    for run_id in test_results["results"]:
        suite_id = test_results["results"][run_id][0].get("suite_id")
        test_cases = [
            result.get("test_case") for result in test_results["results"][run_id]
        ]
        testrail_session.update_test_cases_to_passed(
            test_results.get("project_id"), run_id, suite_id, test_cases
        )


def collect_changes(testrail_session: TestRail, report):
    version_match = FX_VERSION_RE.match(
        report.get("tests")[0].get("metadata").get("fx_version")
    )
    (major, minor, build) = [version_match[n] for n in range(1, 4)]

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

    entry_changes = {"config": config}
    test_results = {"project_id": testrail_project_id, "results": []}
    for test in report.get("tests"):
        (suite_id_str, suite_description) = test.get("metadata").get("suite_id")
        suite_id = int(suite_id_str.replace("S", ""))
        test_case = test.get("metadata").get("test_case")
        config = test.get("metadata").get("machine_config")
        outcome = test.get("outcome")

        suite_entries = [
            entry
            for entry in expected_plan.get("entries")
            if entry.get("suite_id") == suite_id
        ]
        if not suite_entries:
            # If no entry, create entry for suite and platform
            plan_id = expected_plan.get("id")
            logging.info(f"Create entry in plan {plan_id} for suite {suite_id}")
            entry_changes[suite_id] = {
                "plan_id": plan_id,
                "change_type": "create",
                "name": suite_description,
                "case_ids": [int(test_case)],
            }

            # expected_plan["entries"].append(
            # )
        else:
            for entry in suite_entries:
                logging.info(
                    f"For entry {entry['name']}, update if case_ids does not contain {test_case}"
                )
                logging.info(f"If runs list is empty, add placeholder.")
                if not entry.get("runs"):
                    if not entry_changes.get(suite_id):
                        entry_changes[suite_id] = {"entry": entry}
                    if not entry_changes[suite_id].get("change_type"):
                        entry_changes[suite_id]["change_type"] = "update_add_runs"
                    if entry_changes[suite_id].get("cases_to_add_to_run"):
                        entry_changes[suite_id]["cases_to_add_to_run"].append(
                            int(test_case)
                        )
                    else:
                        entry_changes[suite_id]["cases_to_add_to_run"] = [
                            int(test_case)
                        ]
                    continue

                # If you're here, you have runs in your entry
                config_runs = [
                    run for run in entry.get("runs") if run.get("config") == config
                ]
                if not config_runs:
                    if entry_changes[suite_id].get("cases_to_add_to_run"):
                        entry_changes[suite_id]["cases_to_add_to_run"].append(
                            int(test_case)
                        )
                    else:
                        entry_changes[suite_id]["cases_to_add_to_run"] = [
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
                if outcome in ["passed", "xpass"]:
                    logging.info(f"Update run {run_id}")
                    if not test_results["results"].get(run_id):
                        test_results["results"][run_id] = []
                    test_results["results"][run_id].append(
                        {"suite_id": suite_id, "test_case": test_case}
                    )
                else:
                    logging.info(f"Leave run {run_id} alone re: {test_case}")
    return (entry_changes, test_passes)
