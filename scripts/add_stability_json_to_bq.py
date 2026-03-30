#!/usr/bin/env python3

import io
import json
import os
import zipfile
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

import requests
from google.cloud import bigquery


GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO = os.environ["REPO"]
TARGET_WORKFLOW_FILE = os.environ.get("TARGET_WORKFLOW_FILE", "main-stability.yml")

D_RUNS = int(os.environ.get("D_RUNS", "5"))
PLATFORM = os.environ.get("PLATFORM", "all").lower()
INCLUDE_HEADED = os.environ.get("INCLUDE_HEADED", "false").lower() in ("1", "true")

BQ_PROJECT = os.environ["BQ_PROJECT"]
BQ_DATASET = os.environ["BQ_DATASET"]
BQ_TABLE = os.environ.get("BQ_TABLE", "stability_test_events")

if PLATFORM not in {"all", "win", "mac"}:
    raise SystemExit("PLATFORM must be one of: all, win, mac")


def gh_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "stability-json-ingest",
    }


def gh_get_json(url: str, params: Optional[dict] = None) -> dict:
    response = requests.get(url, headers=gh_headers(), params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def gh_get_bytes(url: str) -> bytes:
    response = requests.get(url, headers=gh_headers(), timeout=60)
    response.raise_for_status()
    return response.content


def allowed_artifacts(platform: str, include_headed: bool) -> Set[str]:
    names: Set[str] = set()
    if platform in ("all", "win"):
        names.add("json-win")
        if include_headed:
            names.add("json-win-headed")
    if platform in ("all", "mac"):
        names.add("json-mac")
        if include_headed:
            names.add("json-mac-headed")
    return names


def ensure_table(client: bigquery.Client, table_id: str) -> None:
    try:
        client.get_table(table_id)
        return
    except Exception:
        pass

    schema = [
        bigquery.SchemaField("ingested_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("repo", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("workflow_file", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("run_id", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("run_number", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("run_attempt", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("run_created_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("platform", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("headed", "BOOL", mode="REQUIRED"),
        bigquery.SchemaField("artifact_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("test_nodeid", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("outcome", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("duration", "FLOAT64", mode="NULLABLE"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="ingested_at",
    )
    table.clustering_fields = ["platform", "test_nodeid", "run_id"]
    client.create_table(table)


def list_recent_runs() -> List[dict]:
    url = f"https://api.github.com/repos/{REPO}/actions/workflows/{TARGET_WORKFLOW_FILE}/runs"
    data = gh_get_json(url, params={"per_page": D_RUNS})
    return data.get("workflow_runs", [])


def list_run_artifacts(run_id: int) -> List[dict]:
    url = f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}/artifacts"
    data = gh_get_json(url)
    return data.get("artifacts", [])


def download_artifact_zip(artifact_id: int) -> bytes:
    url = f"https://api.github.com/repos/{REPO}/actions/artifacts/{artifact_id}/zip"
    return gh_get_bytes(url)


def parse_json_reports(zip_bytes: bytes) -> List[dict]:
    reports: List[dict] = []
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    for name in zf.namelist():
        if name.lower().endswith(".json"):
            raw = zf.read(name).decode("utf-8", errors="replace")
            reports.append(json.loads(raw))
    return reports


def artifact_platform(name: str) -> str:
    if "win" in name:
        return "win"
    if "mac" in name:
        return "mac"
    raise ValueError(f"Could not determine platform from artifact name: {name}")


def artifact_is_headed(name: str) -> bool:
    return "headed" in name


def already_ingested_run(
    client: bigquery.Client, table_id: str, run_id: int, artifact_name: str
) -> bool:
    query = f"""
    SELECT COUNT(1) AS c
    FROM `{table_id}`
    WHERE run_id = @run_id
      AND artifact_name = @artifact_name
    """
    job = client.query(
        query,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("run_id", "INT64", run_id),
                bigquery.ScalarQueryParameter("artifact_name", "STRING", artifact_name),
            ]
        ),
    )
    row = next(job.result())
    return row["c"] > 0


def build_rows_for_report(run: dict, artifact_name: str, report: dict) -> List[dict]:
    rows: List[dict] = []
    tests = report.get("tests", [])
    now = datetime.now(timezone.utc).isoformat()

    for test in tests:
        nodeid = test.get("nodeid")
        outcome = (test.get("outcome") or "").lower()
        duration = test.get("duration")

        if not nodeid or not outcome:
            continue

        rows.append(
            {
                "ingested_at": now,
                "repo": REPO,
                "workflow_file": TARGET_WORKFLOW_FILE,
                "run_id": int(run["id"]),
                "run_number": run.get("run_number"),
                "run_attempt": run.get("run_attempt"),
                "run_created_at": run.get("created_at"),
                "platform": artifact_platform(artifact_name),
                "headed": artifact_is_headed(artifact_name),
                "artifact_name": artifact_name,
                "test_nodeid": nodeid,
                "outcome": outcome,
                "duration": duration,
            }
        )

    return rows


def main() -> int:
    client = bigquery.Client(project=BQ_PROJECT)
    table_id = f"{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"
    ensure_table(client, table_id)

    allowed = allowed_artifacts(PLATFORM, INCLUDE_HEADED)
    runs = list_recent_runs()

    all_rows: List[dict] = []

    for run in runs:
        run_id = int(run["id"])
        artifacts = list_run_artifacts(run_id)

        for artifact in artifacts:
            name = artifact["name"]
            if name not in allowed:
                continue
            if artifact.get("expired", False):
                continue

            if already_ingested_run(client, table_id, run_id, name):
                print(f"Skipping already-ingested run_id={run_id}, artifact={name}")
                continue

            zip_bytes = download_artifact_zip(int(artifact["id"]))
            reports = parse_json_reports(zip_bytes)

            for report in reports:
                rows = build_rows_for_report(run, name, report)
                all_rows.extend(rows)

    if not all_rows:
        print("No new rows to insert.")
        return 0

    errors = client.insert_rows_json(table_id, all_rows)
    if errors:
        raise RuntimeError(f"BigQuery insert errors: {errors}")

    print(f"Inserted {len(all_rows)} rows into {table_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
