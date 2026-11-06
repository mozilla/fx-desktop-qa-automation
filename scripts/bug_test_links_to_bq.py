"""
Load desktop Bugzilla bugs created since SINCE_DATE, and the tests that found them,
into BigQuery. A bug links to a test when its summary names an in-tree or STARfox
test, or when a TestRail result lists the bug in its Defects field.

LOAD_MODE=incremental (the default) fetches only what changed since the last load
and merges it in; LOAD_MODE=full rebuilds every table.
"""

import logging
import os
from collections import Counter
from datetime import datetime, timezone

from scripts.bug_test_links.bugzilla import (
    add_treeherder_failures,
    fetch_bugs,
    in_scope,
    search_bugs,
)
from scripts.bug_test_links.common import SINCE_DATE
from scripts.bug_test_links.summary import starfox_name_re, starfox_tests, summary_links
from scripts.bug_test_links.tables import (
    BUGS_TABLE,
    EXECUTIONS_TABLE,
    LINKS_TABLE,
    STAGING_PREFIX,
    STATE_TABLE,
    VIEW,
    bug_row,
    last_load,
    merge_sql,
    replace_table,
    schemas,
)
from scripts.bug_test_links.testrail import TestRailReader, testrail_links

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

LOAD_MODE = os.environ.get("LOAD_MODE") or "incremental"


def collect(cutoff: datetime | None = None, stored: dict | None = None) -> dict:
    """Gather in-scope bugs that link to a test, their links and TestRail
    executions: all of them, or with a cutoff only what changed after it.

    stored holds the IDs of bugs already loaded ("bugs") and of those with a
    TestRail link ("testrail"); an incremental run needs them to decide what to keep.
    """
    stored = stored or {"bugs": set(), "testrail": set()}
    testrail, executions = testrail_links(
        TestRailReader(), int(cutoff.timestamp()) if cutoff else None
    )
    fetched = search_bugs(cutoff.strftime("%Y-%m-%dT%H:%M:%SZ") if cutoff else None)

    # A new TestRail result can point at an unchanged bug that was never loaded.
    if cutoff:
        testrail_bug_ids = {link["bug_id"] for link in testrail}
        unseen = testrail_bug_ids - fetched.keys() - stored["bugs"]
        if unseen:
            fetched.update(fetch_bugs(unseen))

    scoped_bugs = {
        bug_id: bug for bug_id, bug in fetched.items() if in_scope(bug)
    }
    candidates = add_treeherder_failures(scoped_bugs)

    tests = starfox_tests()

    # collect the links from every candidate bug into one list.
    name_re = starfox_name_re(tests)
    links = [
        link for bug in candidates.values()
        for link in summary_links(bug, tests, name_re)
    ]

    # Bugs loaded before and not fetched again keep their earlier scope decision.
    allowed = candidates.keys() | (stored["bugs"] - fetched.keys())
    links.extend(link for link in testrail if link["bug_id"] in allowed)

    linked = {link["bug_id"] for link in links} | stored["testrail"]
    bugs = [candidates[bug_id] for bug_id in sorted(candidates.keys() & linked)]

    logging.info(
        "%d bugs to load, %d links: %s",
        len(bugs),
        len(links),
        dict(Counter(link["source"] for link in links)),
    )
    return {
        "bugs": bugs,
        "links": links,
        "executions": executions,
        "checked": sorted(fetched),
    }


def main() -> int:
    from google.cloud import bigquery

    if LOAD_MODE not in ("incremental", "full"):
        raise SystemExit("LOAD_MODE must be incremental or full")
    project, dataset = os.environ["BQ_PROJECT"], os.environ["BQ_DATASET"]
    table = {name: f"{project}.{dataset}.{name}" for name in schemas()}
    started = datetime.now(timezone.utc)
    ingested_at = started.isoformat()
    client = bigquery.Client(project=project)

    state = last_load(client, table[STATE_TABLE])
    full = LOAD_MODE == "full"
    if not full and (not state or state["since_date"].isoformat() != SINCE_DATE):
        logging.info("No earlier load for since_date %s: loading in full", SINCE_DATE)
        full = True

    if full:
        # Without a state row, a run that fails part way is followed by a full one.
        client.delete_table(table[STATE_TABLE], not_found_ok=True)
        data = collect()
    else:
        logging.info("Loading changes since %s", state["loaded_at"].isoformat())
        stored = {
            "bugs": {
                row["bug_id"]
                for row in client.query(f"SELECT bug_id FROM `{table[BUGS_TABLE]}`")
            },
            "testrail": {
                row["bug_id"]
                for row in client.query(
                    f"SELECT DISTINCT bug_id FROM `{table[LINKS_TABLE]}`"
                    " WHERE source = 'testrail'"
                )
            },
        }
        data = collect(state["loaded_at"], stored)

    rows = {
        BUGS_TABLE: [bug_row(bug, ingested_at) for bug in data["bugs"]],
        LINKS_TABLE: [link | {"ingested_at": ingested_at} for link in data["links"]],
        EXECUTIONS_TABLE: [
            row | {"ingested_at": ingested_at} for row in data["executions"]
        ],
        "checked_bugs": [{"bug_id": bug_id} for bug_id in data["checked"]],
    }
    schema = schemas()

    if full:
        for name in (BUGS_TABLE, LINKS_TABLE, EXECUTIONS_TABLE):
            replace_table(client, table[name], rows[name], *schema[name])
        replace_table(
            client,
            table[STATE_TABLE],
            [{"since_date": SINCE_DATE, "loaded_at": ingested_at, "mode": "full"}],
            *schema[STATE_TABLE],
        )
    else:
        staging = {name: f"{project}.{dataset}.{STAGING_PREFIX}{name}" for name in rows}
        for name, staged in rows.items():
            replace_table(client, staging[name], staged, *schema[name])
        client.query(
            merge_sql(
                {
                    "bugs": table[BUGS_TABLE],
                    "links": table[LINKS_TABLE],
                    "executions": table[EXECUTIONS_TABLE],
                    "state": table[STATE_TABLE],
                    "new_bugs": staging[BUGS_TABLE],
                    "new_links": staging[LINKS_TABLE],
                    "new_executions": staging[EXECUTIONS_TABLE],
                    "checked": staging["checked_bugs"],
                },
                [field.name for field in schema[BUGS_TABLE][0]],
            ),
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("since", "DATE", SINCE_DATE),
                    bigquery.ScalarQueryParameter("loaded_at", "TIMESTAMP", started),
                ]
            ),
        ).result()
        for staged in staging.values():
            client.delete_table(staged, not_found_ok=True)
        logging.info("Merged the changes in one transaction")

    client.query(
        f"""
        CREATE OR REPLACE VIEW `{project}.{dataset}.{VIEW}` AS
        SELECT bug.* EXCEPT (ingested_at), link.* EXCEPT (bug_id, ingested_at)
        FROM `{table[BUGS_TABLE]}` AS bug
        JOIN `{table[LINKS_TABLE]}` AS link USING (bug_id)
        """
    ).result()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
