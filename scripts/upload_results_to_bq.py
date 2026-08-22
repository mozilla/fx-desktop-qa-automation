"""Upload pytest JSON reports to BigQuery for long-term analytics.

Reads the ``report.json`` / ``report_headed.json`` files produced by
pytest-json-report and appends one row per test result to a BigQuery table.

Two properties are deliberate:

* **This script never fails the calling CI job.** Analytics must not break a
  test run, so every error is logged and the process still exits 0.
* **Data auto-expires after one year.** The destination table is day
  partitioned on ``run_started_at`` with a 365 day partition expiration, so
  BigQuery drops each partition a year after the run it describes. There is
  no cleanup job to schedule or maintain.

Table coordinates come from the environment (see ``REQUIRED_VARS``).
Credentials come from Application Default Credentials, set up by the
``google-github-actions/auth`` step that precedes this one in each job --
the same pattern ``add-stability-results-to-bq.yml`` uses. If either is
missing the script logs a notice and exits without doing anything, which
keeps the step harmless on forks and in dry runs.
"""

import glob
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from google.auth.exceptions import DefaultCredentialsError

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Where pytest may have left a report, depending on whether the job has
# already renamed artifacts/ to its per-platform name.
REPORT_GLOBS = [
    "artifacts/report*.json",
    "artifacts-win/report*.json",
    "artifacts-mac/report*.json",
    "artifacts-linux/report*.json",
]

REQUIRED_VARS = ("BQ_PROJECT", "BQ_DATASET")

# One year, in milliseconds. BigQuery deletes a partition this long after the
# date it covers, which is what gives us the 1 year retention guarantee.
PARTITION_EXPIRATION_MS = 365 * 24 * 60 * 60 * 1000

# Long tracebacks are not worth storing in full; keep enough to triage.
MAX_ERROR_CHARS = 4000


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default) or default


def platform_name() -> str:
    """Normalise the runner OS to win/mac/linux."""
    runner_os = env("RUNNER_OS").lower()
    if runner_os.startswith("win"):
        return "win"
    if runner_os in ("macos", "darwin"):
        return "mac"
    if runner_os == "linux":
        return "linux"

    # Fall back to the interpreter when not running on a GitHub runner.
    if sys.platform.startswith("win"):
        return "win"
    if sys.platform == "darwin":
        return "mac"
    return "linux"


def find_reports() -> List[str]:
    paths: List[str] = []
    for pattern in REPORT_GLOBS:
        paths.extend(glob.glob(pattern))
    # A job can rename artifacts/ mid-run, so the same report may match twice.
    return sorted(set(os.path.abspath(p) for p in paths))


def stage_duration(test: Dict[str, Any]) -> Optional[float]:
    """Sum the setup/call/teardown durations.

    pytest-json-report puts duration on each stage, not on the test item, so
    there is no single top-level field to read.
    """
    total = 0.0
    found = False
    for stage in ("setup", "call", "teardown"):
        value = (test.get(stage) or {}).get("duration")
        if isinstance(value, (int, float)):
            total += float(value)
            found = True
    return total if found else None


def error_message(test: Dict[str, Any]) -> Optional[str]:
    """Return the first failure text across the three stages, truncated."""
    for stage in ("call", "setup", "teardown"):
        data = test.get(stage) or {}
        text = data.get("longrepr") or (data.get("crash") or {}).get("message")
        if text:
            return str(text)[:MAX_ERROR_CHARS]
    return None


def build_rows(report: Dict[str, Any], report_path: str) -> List[Dict[str, Any]]:
    """Flatten one JSON report into per-test BigQuery rows."""
    ingested_at = datetime.now(timezone.utc).isoformat()

    # GitHub only exposes the run start time via the workflow context, so the
    # workflow has to pass it through. Fall back to "now" when absent.
    run_started_at = env("GITHUB_RUN_STARTED_AT") or ingested_at

    headed = "headed" in os.path.basename(report_path).lower()

    rows: List[Dict[str, Any]] = []

    for test in report.get("tests") or []:
        nodeid = test.get("nodeid")
        outcome = (test.get("outcome") or "").lower()
        if not nodeid or not outcome:
            continue

        metadata = test.get("metadata") or {}
        suite_id = metadata.get("suite_id") or []
        suite_name = suite_id[1] if len(suite_id) > 1 else None
        test_case = metadata.get("test_case")

        rows.append(
            {
                "ingested_at": ingested_at,
                "run_started_at": run_started_at,
                "repo": env("GITHUB_REPOSITORY"),
                # GITHUB_WORKFLOW is the *entry point* workflow: when main.yml
                # runs as a reusable workflow, this is the caller's name (e.g.
                # "Glean Tests Beta"). workflow_file/job_name below are literals
                # passed by the step, so they always name the workflow that
                # actually ran the tests regardless of reusable-workflow
                # context semantics.
                "workflow": env("GITHUB_WORKFLOW"),
                "workflow_file": env("BQ_WORKFLOW_FILE") or None,
                "job": env("GITHUB_JOB"),
                "job_name": env("BQ_JOB_NAME") or None,
                "run_id": int(env("GITHUB_RUN_ID", "0")) or None,
                "run_number": int(env("GITHUB_RUN_NUMBER", "0")) or None,
                "run_attempt": int(env("GITHUB_RUN_ATTEMPT", "0")) or None,
                "actor": env("GITHUB_ACTOR") or None,
                "ref_name": env("GITHUB_REF_NAME") or None,
                "commit_sha": env("GITHUB_SHA") or None,
                "event_name": env("GITHUB_EVENT_NAME") or None,
                "platform": platform_name(),
                "headed": headed,
                # main.yml puts the split in STARFOX_SPLIT; main-l10n.yml has no
                # split concept, so its steps pass BQ_TEST_SET explicitly.
                "test_set": env("BQ_TEST_SET") or env("STARFOX_SPLIT") or None,
                "fx_channel": env("FX_CHANNEL") or None,
                "fx_version": metadata.get("fx_version"),
                "machine_config": metadata.get("machine_config"),
                "suite_name": suite_name,
                "test_case": str(test_case) if test_case is not None else None,
                "test_nodeid": nodeid,
                "outcome": outcome,
                "duration": stage_duration(test),
                "error_message": error_message(test),
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
        field("error_message", "STRING"),
    ]


def ensure_table(client, table_id: str):
    """Create the table if absent, and enforce the 1 year partition expiry.

    The expiry is re-applied to pre-existing tables too, so a table created
    before this script existed still picks up the retention policy.
    """
    from google.cloud import bigquery
    from google.api_core.exceptions import NotFound

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


def upload(rows: List[Dict[str, Any]]) -> None:
    from google.cloud import bigquery

    project = os.environ["BQ_PROJECT"]
    dataset = os.environ["BQ_DATASET"]
    table = env("BQ_TABLE", "test_results")
    table_id = f"{project}.{dataset}.{table}"

    # Credentials come from Application Default Credentials, which the
    # "Auth to Google Cloud" step provides via google-github-actions/auth.
    # Locally, `gcloud auth application-default login` works the same way.
    client = bigquery.Client(project=project)
    ensure_table(client, table_id)

    # A load job is used rather than insert_rows_json: batch loads are free and
    # have no streaming buffer, which keeps rows immediately queryable.
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

        rows: List[Dict[str, Any]] = []
        for path in reports:
            try:
                with open(path, encoding="utf-8", errors="replace") as handle:
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
        # The "Auth to Google Cloud" step is continue-on-error, so a missing or
        # rejected credential lands here. Not worth an ERROR: the test results
        # themselves are unaffected.
        logging.info("Skipping BigQuery upload; no Google credentials available.")

    except Exception as exc:  # noqa: BLE001 - must never fail the CI job
        logging.error("BigQuery upload failed, continuing anyway: %s", exc)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
