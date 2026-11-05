"""BigQuery tables of the loader: rows, schemas, full replace and incremental merge."""

import logging
from collections import Counter

from scripts.bug_test_links.bugzilla import BUGZILLA_URL, is_intermittent

BUGS_TABLE = "bugzilla_bugs"
LINKS_TABLE = "bug_test_links"
EXECUTIONS_TABLE = "testrail_executions"
STATE_TABLE = "bug_test_links_state"
STAGING_PREFIX = "staging_"
VIEW = "desktop_bugs_with_tests"


def bug_row(bug: dict, ingested_at: str) -> dict:
    failures = bug.get("desktop_failures") or Counter()
    return {
        "bug_id": bug["id"],
        "summary": bug["summary"],
        "product": bug["product"],
        "component": bug["component"],
        "platform": bug["platform"],
        "op_sys": bug["op_sys"],
        "status": bug["status"],
        "resolution": bug["resolution"] or None,
        "type": bug.get("type"),
        "severity": bug.get("severity"),
        "priority": bug.get("priority"),
        "keywords": bug["keywords"],
        "regressed_by": bug.get("regressed_by") or [],
        "firefox_status": [
            {"version": key.removeprefix("cf_status_firefox"), "status": value}
            for key, value in bug.items()
            if key.startswith("cf_status_firefox") and value not in (None, "---")
        ],
        "is_intermittent": is_intermittent(bug),
        "desktop_failure_count": sum(failures.values()) if failures else None,
        "desktop_failure_platforms": sorted(failures),
        "creation_time": bug["creation_time"],
        "last_change_time": bug.get("last_change_time"),
        "url": f"{BUGZILLA_URL}/show_bug.cgi?id={bug['id']}",
        "ingested_at": ingested_at,
    }


def schemas():
    from google.cloud import bigquery

    def field(name, field_type, mode="NULLABLE", fields=()):
        return bigquery.SchemaField(name, field_type, mode=mode, fields=fields)

    bugs = [
        field("bug_id", "INT64", "REQUIRED"),
        field("summary", "STRING"),
        field("product", "STRING"),
        field("component", "STRING"),
        field("platform", "STRING"),
        field("op_sys", "STRING"),
        field("status", "STRING"),
        field("resolution", "STRING"),
        field("type", "STRING"),
        field("severity", "STRING"),
        field("priority", "STRING"),
        field("keywords", "STRING", "REPEATED"),
        field("regressed_by", "INT64", "REPEATED"),
        field(
            "firefox_status",
            "RECORD",
            "REPEATED",
            (field("version", "STRING"), field("status", "STRING")),
        ),
        field("is_intermittent", "BOOL"),
        field("desktop_failure_count", "INT64"),
        field("desktop_failure_platforms", "STRING", "REPEATED"),
        field("creation_time", "TIMESTAMP", "REQUIRED"),
        field("last_change_time", "TIMESTAMP"),
        field("url", "STRING"),
        field("ingested_at", "TIMESTAMP", "REQUIRED"),
    ]
    links = [
        field("bug_id", "INT64", "REQUIRED"),
        field("source", "STRING", "REQUIRED"),
        field("test_key", "STRING", "REQUIRED"),
        field("test_key_type", "STRING", "REQUIRED"),
        field("case_id", "INT64"),
        field("case_title", "STRING"),
        field("suite_id", "INT64"),
        field("release", "STRING"),
        field("channel_milestone", "STRING"),
        field("channel", "STRING"),
        field("plan_id", "INT64"),
        field("plan_name", "STRING"),
        field("entry_name", "STRING"),
        field("run_id", "INT64"),
        field("run_name", "STRING"),
        field("run_config", "STRING"),
        field("fx_version", "STRING"),
        field("testrail_test_id", "INT64"),
        field("result_id", "INT64"),
        field("result_status", "STRING"),
        field("result_created_at", "TIMESTAMP"),
        field("ingested_at", "TIMESTAMP", "REQUIRED"),
    ]
    executions = [
        field("result_id", "INT64", "REQUIRED"),
        field("case_id", "INT64", "REQUIRED"),
        field("executed_on", "DATE", "REQUIRED"),
        field("ingested_at", "TIMESTAMP", "REQUIRED"),
    ]
    checked = [field("bug_id", "INT64", "REQUIRED")]
    state = [
        field("since_date", "DATE", "REQUIRED"),
        field("loaded_at", "TIMESTAMP", "REQUIRED"),
        field("mode", "STRING", "REQUIRED"),
    ]
    return {
        BUGS_TABLE: (bugs, ["product", "component"]),
        LINKS_TABLE: (links, ["source", "test_key"]),
        EXECUTIONS_TABLE: (executions, ["case_id"]),
        "checked_bugs": (checked, None),
        STATE_TABLE: (state, None),
    }


def replace_table(client, table_id: str, rows: list[dict], schema, clustering):
    """Recreate a table with the given rows (none is fine)."""
    from google.cloud import bigquery

    client.delete_table(table_id, not_found_ok=True)
    table = bigquery.Table(table_id, schema=schema)
    table.clustering_fields = clustering
    client.create_table(table)
    if rows:
        client.load_table_from_json(
            rows,
            table_id,
            job_config=bigquery.LoadJobConfig(
                schema=schema,
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            ),
        ).result()
    logging.info("Loaded %d rows into %s", len(rows), table_id)


def merge_sql(tables: dict[str, str], bug_columns: list[str]) -> str:
    """One transaction that applies the staging tables to the loaded ones."""
    t = tables
    updates = ", ".join(
        f"{name} = S.{name}" for name in bug_columns if name != "bug_id"
    )
    return f"""
    BEGIN TRANSACTION;

    -- Bugs fetched again get fresh summary links; bugs now dropped lose every link.
    DELETE FROM `{t["links"]}`
    WHERE bug_id IN (SELECT bug_id FROM `{t["checked"]}`)
      AND (source != 'testrail'
           OR bug_id NOT IN (SELECT bug_id FROM `{t["new_bugs"]}`));
    DELETE FROM `{t["bugs"]}`
    WHERE bug_id IN (SELECT bug_id FROM `{t["checked"]}`)
      AND bug_id NOT IN (SELECT bug_id FROM `{t["new_bugs"]}`);

    MERGE INTO `{t["bugs"]}` AS T USING `{t["new_bugs"]}` AS S ON T.bug_id = S.bug_id
    WHEN MATCHED THEN UPDATE SET {updates}
    WHEN NOT MATCHED THEN INSERT ROW;

    INSERT INTO `{t["links"]}`
    SELECT * FROM `{t["new_links"]}` WHERE source != 'testrail';
    MERGE INTO `{t["links"]}` AS T
    USING (SELECT * FROM `{t["new_links"]}` WHERE source = 'testrail') AS S
    ON T.result_id = S.result_id AND T.bug_id = S.bug_id
    WHEN NOT MATCHED THEN INSERT ROW;

    MERGE INTO `{t["executions"]}` AS T USING `{t["new_executions"]}` AS S
    ON T.result_id = S.result_id
    WHEN NOT MATCHED THEN INSERT ROW;

    DELETE FROM `{t["state"]}` WHERE TRUE;
    INSERT INTO `{t["state"]}` (since_date, loaded_at, mode)
    VALUES (@since, @loaded_at, 'incremental');

    COMMIT TRANSACTION;
    """


def last_load(client, table_id: str) -> dict | None:
    """Return the state row of the last load, or None if there wasn't one."""
    from google.api_core.exceptions import NotFound

    try:
        rows = list(client.query(f"SELECT * FROM `{table_id}`").result())
    except NotFound:
        return None
    return dict(rows[0]) if rows else None
