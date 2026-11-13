"""Read failed TestRail results that list a bug, and valid executions."""

import logging
import os
import re
from time import sleep
from typing import Any, Iterator

from modules.testrail import APIError, TestRail
from modules.testrail_integration import PLAN_NAME_RE, TESTRAIL_FX_DESK_PRJ
from scripts.bug_test_links.common import epoch_to_iso, since_epoch

# A result with any other status is a run that gave a verdict.
NOT_EXECUTED_STATUSES = {"untested", "blocked", "retest", "skipped"}
# Only a failed result's Defects field links a bug to the case.
FAILED_STATUSES = {"failed", "failed (new)"}
TESTRAIL_PAGE = 250
FX_VERSION_RE = re.compile(r"\d+\.\d+(?:b\d+|\.\d+)?(?:-build\d+)?")
BUG_ID_RE = re.compile(r"(?<![\w-])(\d{6,8})(?!\w)")


def bug_ids(text: str | None) -> set[int]:
    return {int(match) for match in BUG_ID_RE.findall(text or "")}


class TestRailReader:
    """Paged, rate-limit-aware reads from the Firefox Desktop TestRail project."""

    def __init__(self):
        self.session = TestRail(
            os.environ["TESTRAIL_BASE_URL"],
            os.environ["TESTRAIL_USERNAME"],
            os.environ["TESTRAIL_API_KEY"],
        )

    def get(self, uri: str, retries: int = 5) -> Any:
        for attempt in range(retries):
            try:
                return self.session.client.send_get(uri)
            except APIError as error:
                if "HTTP 429" not in str(error) or attempt == retries - 1:
                    raise
                logging.info("TestRail rate limit hit, waiting a minute")
                sleep(60)

    def paged(self, uri: str, key: str) -> Iterator[dict]:
        """Yield every item of a paginated list endpoint."""
        offset = 0
        while True:
            page = self.get(f"{uri}&limit={TESTRAIL_PAGE}&offset={offset}")
            items = page.get(key, []) if isinstance(page, dict) else page
            yield from items
            if len(items) < TESTRAIL_PAGE:
                return
            offset += TESTRAIL_PAGE

    def milestones(self) -> dict[int, dict]:
        """Map milestone id to its name and its parent's name."""
        names, parents = {}, {}

        def add(milestone: dict):
            names[milestone["id"]] = milestone["name"]
            parents[milestone["id"]] = milestone.get("parent_id")
            for child in milestone.get("milestones") or []:
                add(child | {"parent_id": milestone["id"]})

        for milestone in self.paged(
            f"get_milestones/{TESTRAIL_FX_DESK_PRJ}", "milestones"
        ):
            add(milestone)
        return {
            milestone_id: {"name": name, "parent": names.get(parents[milestone_id])}
            for milestone_id, name in names.items()
        }

    def statuses(self) -> dict[int, str]:
        return {status["id"]: status["label"] for status in self.get("get_statuses")}


def milestone_context(milestones: dict[int, dict], milestone_id: int | None) -> dict:
    """Return the release ("Firefox 150") and channel milestone ("Beta 150")."""
    milestone = milestones.get(milestone_id) or {}
    if milestone.get("parent"):
        return {"release": milestone["parent"], "channel_milestone": milestone["name"]}
    return {"release": milestone.get("name"), "channel_milestone": None}


def finished_before(item: dict, cutoff: int | None) -> bool:
    """True if a plan or run was completed before cutoff, so has no newer results."""
    return bool(
        cutoff and item.get("is_completed") and (item.get("completed_on") or 0) < cutoff
    )


def runs_since(
    reader: TestRailReader, milestones: dict[int, dict], cutoff: int | None = None
) -> Iterator:
    """Yield every run created since SINCE_DATE, in a plan or standalone, with
    context; with a cutoff, skip runs completed before it."""
    created_after = since_epoch()
    for plan in reader.paged(
        f"get_plans/{TESTRAIL_FX_DESK_PRJ}&created_after={created_after}", "plans"
    ):
        if finished_before(plan, cutoff):
            continue
        plan_channel = PLAN_NAME_RE.match(plan["name"] or "")
        context = {
            "plan_id": plan["id"],
            "plan_name": plan["name"],
            "channel": plan_channel.group(1) if plan_channel else None,
            **milestone_context(milestones, plan.get("milestone_id")),
        }
        for entry in reader.get(f"get_plan/{plan['id']}").get("entries", []):
            for run in entry.get("runs", []):
                if not finished_before(run, cutoff):
                    yield run | {"entry_name": entry["name"]}, context

    for run in reader.paged(
        f"get_runs/{TESTRAIL_FX_DESK_PRJ}&created_after={created_after}", "runs"
    ):
        if finished_before(run, cutoff):
            continue
        yield (
            run | {"entry_name": None},
            {
                "plan_id": None,
                "plan_name": None,
                "channel": None,
                **milestone_context(milestones, run.get("milestone_id")),
            },
        )


def testrail_links(
    reader: TestRailReader, cutoff: int | None = None
) -> tuple[list[dict], list[dict]]:
    """Return one link per bug in a failed result's Defects, with its run's
    release context, and one row per valid execution; with a cutoff, only for
    results created after it."""
    milestones = reader.milestones()
    statuses = reader.statuses()
    links = []
    executions = []
    newer = f"&created_after={cutoff}" if cutoff else ""
    for run, context in runs_since(reader, milestones, cutoff):
        results = list(
            reader.paged(f"get_results_for_run/{run['id']}{newer}", "results")
        )
        if not results:
            continue

        tests = {
            test["id"]: test for test in reader.paged(f"get_tests/{run['id']}", "tests")
        }
        fx_version = FX_VERSION_RE.search(run["name"] or "")
        for result in results:
            test = tests.get(result["test_id"], {})
            status = statuses.get(result.get("status_id"))
            if (
                test.get("case_id")
                and (status or "").lower() not in NOT_EXECUTED_STATUSES
            ):
                executions.append(
                    {
                        "result_id": result["id"],
                        "case_id": test["case_id"],
                        "executed_on": (epoch_to_iso(result.get("created_on")) or "")[
                            :10
                        ],
                    }
                )
            if (status or "").lower() not in FAILED_STATUSES:
                continue
            for bug_id in bug_ids(result.get("defects")):
                links.append(
                    context
                    | {
                        "bug_id": bug_id,
                        "source": "testrail",
                        "test_key": f"C{test.get('case_id')}",
                        "test_key_type": "testrail_case",
                        "case_id": test.get("case_id"),
                        "case_title": test.get("title"),
                        "suite_id": run.get("suite_id"),
                        "entry_name": run["entry_name"],
                        "run_id": run["id"],
                        "run_name": run["name"],
                        "run_config": run.get("config"),
                        "fx_version": result.get("version")
                        or (fx_version.group(0) if fx_version else None),
                        "testrail_test_id": result["test_id"],
                        "result_id": result["id"],
                        "result_status": status,
                        "result_created_at": epoch_to_iso(result.get("created_on")),
                    }
                )
    logging.info(
        "Found %d TestRail result links and %d executions", len(links), len(executions)
    )
    return links, executions
