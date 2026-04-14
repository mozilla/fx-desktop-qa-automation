#!/usr/bin/env python3

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

import requests
import yaml
from google.cloud import bigquery
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


BQ_PROJECT = os.environ["BQ_PROJECT"]
BQ_DATASET = os.environ["BQ_DATASET"]
BQ_TABLE = os.environ.get("BQ_TABLE", "stability_test_events")

REPO = os.environ["REPO"]
WORKFLOW_FILE = os.environ.get("WORKFLOW_FILE", "main-stability.yml")

PLATFORM = os.environ["PLATFORM"].lower()
RUNS = int(os.environ.get("RUNS", "5"))
INCLUDE_HEADED = os.environ.get("INCLUDE_HEADED", "false").lower() in (
    "1",
    "true",
    "yes",
)

SLACK_KEY = os.environ["SLACK_KEY"]
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL", "C07AHPJ525V")

MANIFEST_PATH = Path("manifests/key.yaml")

if PLATFORM not in {"win", "mac"}:
    raise SystemExit("PLATFORM must be win or mac")


def load_manifest() -> dict:
    with MANIFEST_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def manifest_entries(manifest: dict):
    """
    Yield tuples:
      (test_nodeid, result_field)

    Supports:
      suite:
        test_name:
          result: ...
          splits: ...

    and:
      suite:
        test_file:
          test_subtest:
            result: ...
            splits: ...
    """
    for suite, suite_blob in manifest.items():
        if not isinstance(suite_blob, dict):
            continue

        for testfile, entry in suite_blob.items():
            if not isinstance(entry, dict):
                continue

            # file-level entry
            if "splits" in entry:
                nodeid = f"tests/{suite}/{testfile}.py"
                yield nodeid, entry.get("result")
                continue

            # subtest-level entry
            for subtest_name, subentry in entry.items():
                if not str(subtest_name).startswith("test_"):
                    continue
                if not isinstance(subentry, dict):
                    continue
                if "splits" not in subentry:
                    continue

                nodeid = f"tests/{suite}/{testfile}.py::{subtest_name}"
                yield nodeid, subentry.get("result")


def manifest_state_for_platform(result_field, platform: str) -> Optional[str]:
    """
    Manifest supports:
      result: pass
      result: flaky
      result: unstable
    or:
      result:
        win: pass
        mac: unstable
        linux: pass
    """
    if isinstance(result_field, str):
        return result_field.lower()

    if isinstance(result_field, dict):
        value = result_field.get(platform)
        if isinstance(value, str):
            return value.lower()

    return None


def classify_recent(statuses_oldest_to_newest: List[str]) -> str:
    """
    Rules:
    - if the last 2 consecutive executions are fail/fail => unstable
    - else if the last 2 are a mix of fail/pass => flaky
    - else if the last 2 are pass/pass but there is one or more fail within the last N => flaky
    - else pass

    If fewer than 2 executions exist, return unknown.
    """
    if len(statuses_oldest_to_newest) < 2:
        return "unknown"

    last_two = statuses_oldest_to_newest[-2:]

    if last_two == ["fail", "fail"]:
        return "unstable"

    if set(last_two) == {"pass", "fail"}:
        return "flaky"

    if last_two == ["pass", "pass"]:
        if any(status == "fail" for status in statuses_oldest_to_newest[:-2]):
            return "flaky"
        return "pass"

    return "unknown"


def fetch_classifications_from_bq(
    client: bigquery.Client,
    repo: str,
    workflow_file: str,
    platform: str,
    runs: int,
    include_headed: bool,
) -> List[Dict[str, object]]:
    table_id = f"{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"

    query = f"""
    WITH latest_runs AS (
      SELECT DISTINCT run_id, run_created_at
      FROM `{table_id}`
      WHERE repo = @repo
        AND workflow_file = @workflow_file
        AND platform = @platform
        AND (@include_headed OR headed = FALSE)
      ORDER BY run_created_at DESC
      LIMIT @runs
    ),
    per_run_test AS (
      SELECT
        e.test_nodeid,
        e.run_id,
        e.run_created_at,
        IF(
          COUNTIF(LOWER(e.outcome) IN ('failed', 'error')) > 0,
          'fail',
          'pass'
        ) AS normalized_status
      FROM `{table_id}` e
      JOIN latest_runs r
        ON e.run_id = r.run_id
      WHERE e.repo = @repo
        AND e.workflow_file = @workflow_file
        AND e.platform = @platform
        AND (@include_headed OR e.headed = FALSE)
      GROUP BY e.test_nodeid, e.run_id, e.run_created_at
    )
    SELECT
      test_nodeid,
      ARRAY_AGG(normalized_status ORDER BY run_created_at ASC) AS statuses
    FROM per_run_test
    GROUP BY test_nodeid
    ORDER BY test_nodeid
    """

    job = client.query(
        query,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("repo", "STRING", repo),
                bigquery.ScalarQueryParameter("workflow_file", "STRING", workflow_file),
                bigquery.ScalarQueryParameter("platform", "STRING", platform),
                bigquery.ScalarQueryParameter("include_headed", "BOOL", include_headed),
                bigquery.ScalarQueryParameter("runs", "INT64", runs),
            ]
        ),
    )

    results: List[Dict[str, object]] = []
    for row in job.result():
        statuses = list(row["statuses"])
        state = classify_recent(statuses)
        results.append(
            {
                "test_nodeid": row["test_nodeid"],
                "statuses": statuses,
                "state": state,
            }
        )

    return results


def build_changes(
    manifest: dict,
    computed: List[Dict[str, object]],
    platform: str,
) -> List[Dict[str, object]]:
    manifest_map: Dict[str, Optional[str]] = {}

    for nodeid, result_field in manifest_entries(manifest):
        manifest_map[nodeid] = manifest_state_for_platform(result_field, platform)

    changes: List[Dict[str, object]] = []

    for item in computed:
        nodeid = item["test_nodeid"]
        new_state = item["state"]
        statuses = item["statuses"]
        current_state = manifest_map.get(nodeid)

        if current_state is None:
            continue
        if new_state == "unknown":
            continue
        if new_state == current_state:
            continue

        fail_count = sum(1 for s in statuses if s == "fail")
        changes.append(
            {
                "test_nodeid": nodeid,
                "manifest_state": current_state,
                "computed_state": new_state,
                "statuses": statuses,
                "fail_count": fail_count,
            }
        )

    return changes


def build_slack_blocks(
    changes: List[Dict[str, object]], platform: str, runs: int
) -> List[dict]:
    header_text = f"Stability state changes for {platform} (last {runs} runs)"

    if not changes:
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{header_text}*\nNo test state changes detected.",
                },
            }
        ]

    severity_order = {"pass": 0, "flaky": 1, "unstable": 2}
    changes_sorted = sorted(
        changes,
        key=lambda x: (
            severity_order.get(str(x["computed_state"]), -1)
            - severity_order.get(str(x["manifest_state"]), -1),
            x["fail_count"],
        ),
        reverse=True,
    )

    blocks: List[dict] = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (f"*{header_text}*\nChanged tests: *{len(changes_sorted)}*"),
            },
        },
        {"type": "divider"},
    ]

    for change in changes_sorted[:50]:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*{change['test_nodeid']}*\n"
                        f"`{change['manifest_state']}` -> `{change['computed_state']}`\n"
                        f"fails: `{change['fail_count']}/{len(change['statuses'])}`\n"
                        f"statuses: `{change['statuses']}`"
                    ),
                },
            }
        )

    if len(changes_sorted) > 50:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"...and {len(changes_sorted) - 50} more",
                },
            }
        )

    return blocks


def send_slack_message(
    changes: List[Dict[str, object]], platform: str, runs: int
) -> None:
    print("Trying to send Slack message...")
    client = WebClient(token=SLACK_KEY)
    blocks = build_slack_blocks(changes, platform, runs)

    try:
        client.chat_postMessage(
            channel=SLACK_CHANNEL,
            text="Important update from ACTIONS...",
            blocks=blocks,
        )
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")
        raise


def main() -> int:
    manifest = load_manifest()
    client = bigquery.Client(project=BQ_PROJECT)

    computed = fetch_classifications_from_bq(
        client=client,
        repo=REPO,
        workflow_file=WORKFLOW_FILE,
        platform=PLATFORM,
        runs=RUNS,
        include_headed=INCLUDE_HEADED,
    )

    changes = build_changes(manifest, computed, PLATFORM)

    send_slack_message(changes, PLATFORM, RUNS)

    print(json.dumps(changes, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
