"""
Upload pytest JSON reports to BigQuery for long-term analytics,
storing one row per test for one year.
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from google.auth.exceptions import DefaultCredentialsError

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


REPORT_GLOBS = [
    "artifacts/report*.json",
    "artifacts-win/report*.json",
    "artifacts-mac/report*.json",
    "artifacts-linux/report*.json",
]

DEFAULT_BQ_TABLE = "test_results"
REQUIRED_VARS = ("BQ_PROJECT", "BQ_DATASET")


PARTITION_EXPIRATION_MS = 365 * 24 * 60 * 60 * 1000


def env(name: str, default: str = "") -> str:
    return os.environ.get(name) or default


def platform_name() -> str:
    """Normalise the runner OS to win/mac/linux."""
    runner_os = env("RUNNER_OS").lower()
    if runner_os.startswith("win"):
        return "win"
    if runner_os in ("macos", "darwin"):
        return "mac"
    if runner_os == "linux":
        return "linux"

    if sys.platform.startswith("win"):
        return "win"
    if sys.platform == "darwin":
        return "mac"
    return "linux"


def find_reports() -> list[Path]:
    return sorted(
        {path.resolve() for pattern in REPORT_GLOBS for path in Path().glob(pattern)}
    )


def test_duration(test: dict[str, Any]) -> float | None:
    """Return total setup, call, and teardown duration."""
    durations = [
        duration
        for stage in ("setup", "call", "teardown")
        if isinstance(
            duration := (test.get(stage) or {}).get("duration"),
            (int, float),
        )
    ]
    return sum(durations) if durations else None


def build_rows(
    report: dict[str, Any],
    report_path: str,
) -> list[dict[str, Any]]:
    """Flatten one pytest JSON report into per-test BigQuery rows."""
    ingested_at = datetime.now(timezone.utc).isoformat()

    common = {
        "ingested_at": ingested_at,
        "run_started_at": env("GITHUB_RUN_STARTED_AT") or ingested_at,
        "repo": env("GITHUB_REPOSITORY") or None,
        "workflow": env("GITHUB_WORKFLOW") or None,
        "workflow_file": env("BQ_WORKFLOW_FILE") or None,
        "job": env("GITHUB_JOB") or None,
        "job_name": env("BQ_JOB_NAME") or None,
        "run_id": int(env("GITHUB_RUN_ID", "0")) or None,
        "run_number": int(env("GITHUB_RUN_NUMBER", "0")) or None,
        "run_attempt": int(env("GITHUB_RUN_ATTEMPT", "0")) or None,
        "actor": env("GITHUB_ACTOR") or None,
        "ref_name": env("GITHUB_REF_NAME") or None,
        "commit_sha": env("GITHUB_SHA") or None,
        "event_name": env("GITHUB_EVENT_NAME") or None,
        "platform": platform_name(),
        "headed": "headed" in os.path.basename(report_path).lower(),
        "test_set": env("BQ_TEST_SET") or env("STARFOX_SPLIT") or None,
        "fx_channel": env("FX_CHANNEL") or None,
    }

    rows = []

    for test in report.get("tests", []):
        nodeid = test.get("nodeid")
        outcome = test.get("outcome")

        if not nodeid or not outcome:
            continue

        metadata = test.get("metadata") or {}
        suite_id = metadata.get("suite_id") or []

        rows.append(
            common
            | {
                "fx_version": metadata.get("fx_version"),
                "machine_config": metadata.get("machine_config"),
                "suite_name": (
                    suite_id[1]
                    if isinstance(suite_id, (list, tuple)) and len(suite_id) > 1
                    else None
                ),
                "test_case": (
                    str(metadata["test_case"])
                    if metadata.get("test_case") is not None
                    else None
                ),
                "test_nodeid": nodeid,
                "outcome": outcome.lower(),
                "duration": test_duration(test),
            }
        )

    return rows


def table_schema():
    from google.cloud import bigquery

    def field(name, field_type, mode="NULLABLE"):
        return bigquery.SchemaField(name, field_type, mode=mode)

    return [
        field("ingested_at", "TIMESTAMP", "REQUIRED"),
        field("run_started_at", "TIMESTAMP", "REQUIRED"),
        field("repo", "STRING"),
        field("workflow", "STRING"),
        field("workflow_file", "STRING"),
        field("job", "STRING"),
        field("job_name", "STRING"),
        field("run_id", "INT64"),
        field("run_number", "INT64"),
        field("run_attempt", "INT64"),
        field("actor", "STRING"),
        field("ref_name", "STRING"),
        field("commit_sha", "STRING"),
        field("event_name", "STRING"),
        field("platform", "STRING"),
        field("headed", "BOOL"),
        field("test_set", "STRING"),
        field("fx_channel", "STRING"),
        field("fx_version", "STRING"),
        field("machine_config", "STRING"),
        field("suite_name", "STRING"),
        field("test_case", "STRING"),
        field("test_nodeid", "STRING", "REQUIRED"),
        field("outcome", "STRING", "REQUIRED"),
        field("duration", "FLOAT64"),
    ]


def ensure_table(client, table_id: str):
    """Create the table if absent, and enforce the one year partition expiry."""
    from google.api_core.exceptions import NotFound
    from google.cloud import bigquery

    partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="run_started_at",
        expiration_ms=PARTITION_EXPIRATION_MS,
    )

    try:
        table = client.get_table(table_id)
    except NotFound:
        table = bigquery.Table(table_id, schema=table_schema())
        table.time_partitioning = partitioning
        table.clustering_fields = [
            "workflow_file",
            "platform",
            "suite_name",
            "outcome",
        ]
        table = client.create_table(table)
        logging.info("Created table %s (365 day partition expiration)", table_id)
        return table

    current = table.time_partitioning
    if current is None or current.expiration_ms != PARTITION_EXPIRATION_MS:
        table.time_partitioning = partitioning
        table = client.update_table(table, ["time_partitioning"])
        logging.info("Updated %s to a 365 day partition expiration", table_id)

    return table


def upload(rows: list[dict[str, Any]]) -> None:
    from google.cloud import bigquery

    project = os.environ["BQ_PROJECT"]
    dataset = os.environ["BQ_DATASET"]
    table = env("BQ_TABLE", DEFAULT_BQ_TABLE)
    table_id = f"{project}.{dataset}.{table}"

    client = bigquery.Client(project=project)
    ensure_table(client, table_id)

    job = client.load_table_from_json(
        rows,
        table_id,
        job_config=bigquery.LoadJobConfig(
            schema=table_schema(),
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            # Let a newly added column land in a table created by an older
            # version of this script instead of failing the load.
            schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION],
        ),
    )
    job.result()

    logging.info("Loaded %d rows into %s", len(rows), table_id)


def main() -> int:
    missing = [name for name in REQUIRED_VARS if not env(name)]
    if missing:
        logging.info(
            "Skipping BigQuery upload; not configured (%s)", ", ".join(missing)
        )
        return 0

    try:
        reports = find_reports()
        if not reports:
            logging.info("No pytest JSON report found; nothing to upload.")
            return 0

        rows: list[dict[str, Any]] = []

        for path in reports:
            try:
                with path.open(encoding="utf-8", errors="replace") as handle:
                    report = json.load(handle)
            except (OSError, ValueError) as exc:
                logging.warning("Could not read %s: %s", path, exc)
                continue

            report_rows = build_rows(report, path)
            logging.info("%s -> %d rows", path, len(report_rows))
            rows.extend(report_rows)

        if not rows:
            logging.info("Reports contained no test results; nothing to upload.")
            return 0

        upload(rows)

    except DefaultCredentialsError:
        logging.info("Skipping BigQuery upload; no Google credentials available.")

    except Exception as exc:
        logging.error("BigQuery upload failed, continuing anyway: %s", exc)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
