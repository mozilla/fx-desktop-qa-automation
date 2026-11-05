"""
Score each test's yield from the bug_test_links and bugzilla_bugs tables and
write it to the test_yield table:

    Yield = 100 * (wU*U + wF*F + wS*S + wR*R) / (wU + wF + wS + wR)

Coverage (C) is left out until its inputs exist. Run with
`uv run python -m scripts.test_yield_to_bq` after `scripts.bug_test_links_to_bq`.
"""

import logging
import math
import os
from bisect import bisect_right
from collections import Counter, defaultdict
from datetime import date, datetime, timezone

import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

SINCE_DATE = os.environ.get("SINCE_DATE") or "2026-10-13"
LINKS_TABLE = "bug_test_links"
BUGS_TABLE = "bugzilla_bugs"
EXECUTIONS_TABLE = "testrail_executions"
STARFOX_RESULTS_TABLE = "test_results"
YIELD_TABLE = "test_yield"
RELEASES_URL = (
    "https://product-details.mozilla.org/1.0/firefox_history_major_releases.json"
)
VERSIONS_URL = "https://product-details.mozilla.org/1.0/firefox_versions.json"

DEFAULT_WEIGHTS = {"U": 0.25, "F": 0.20, "S": 0.30, "R": 0.15}
SEVERITY_WEIGHT = float(os.environ.get("YIELD_SEVERITY_WEIGHT") or 0.6)
# Unset severity or priority ("--") counts as 0.
SEVERITY = {"S1": 1.0, "S2": 0.7, "S3": 0.4, "S4": 0.2, "N/A": 0.1}
PRIORITY = {"P1": 1.0, "P2": 0.8, "P3": 0.5, "P4": 0.25, "P5": 0.1}
# Resolutions meaning the report wasn't a new, real bug.
NOT_A_BUG = {"INVALID", "WORKSFORME", "INCOMPLETE", "DUPLICATE"}
# STARfox CI outcomes where the test ran to a verdict; rerun is fail-then-pass.
STARFOX_EXECUTED = ("passed", "failed", "rerun")


def weights() -> dict[str, float]:
    """Read weights from YIELD_WEIGHTS, e.g. "U=0.25,F=0.2,S=0.3,R=0.15"."""
    raw = os.environ.get("YIELD_WEIGHTS")
    if not raw:
        return DEFAULT_WEIGHTS
    parsed = {
        key.strip(): float(value)
        for key, value in (part.split("=") for part in raw.split(","))
    }
    if set(parsed) != set(DEFAULT_WEIGHTS) or min(parsed.values()) <= 0:
        raise SystemExit("YIELD_WEIGHTS needs positive weights for U, F, S and R")
    return parsed


def release_dates() -> list[tuple[date, int]]:
    """Return (release date, major version) for every release, next one included."""
    history = requests.get(RELEASES_URL, timeout=60).json()
    versions = requests.get(VERSIONS_URL, timeout=60).json()
    releases = [
        (date.fromisoformat(day), int(version.split(".")[0]))
        for version, day in history.items()
    ]
    latest = max(version for _, version in releases)
    releases.append((date.fromisoformat(versions["NEXT_RELEASE_DATE"]), latest + 1))
    return sorted(releases)


def cycle_of(day: date, releases: list[tuple[date, int]]) -> int:
    """Return the version that ships at the end of the cycle containing day."""
    index = bisect_right([released for released, _ in releases], day)
    if index == len(releases):
        return releases[-1][1] + 1
    return releases[index][1]


def bug_impact(bug: dict) -> float:
    """Weighted severity and priority on a 0-1 scale; unset counts as 0."""
    return SEVERITY_WEIGHT * SEVERITY.get(bug.get("severity"), 0.0) + (
        1 - SEVERITY_WEIGHT
    ) * PRIORITY.get(bug.get("priority"), 0.0)


def is_regression(bug: dict) -> bool:
    return "regression" in (bug.get("keywords") or []) or bool(bug.get("regressed_by"))


def normalized(values: dict, scale=lambda value: value) -> dict:
    """Divide each value by the largest one, after scale; all zeros stay zero."""
    top = max((scale(value) for value in values.values()), default=0)
    return {key: scale(value) / top if top else 0.0 for key, value in values.items()}


def yield_score(parts: dict[str, float | None], weights: dict[str, float]) -> float:
    """100 * the weighted sum of the components, with the weights scaled to sum
    to 1; missing components (None) are left out before scaling."""
    available = [name for name, part in parts.items() if part is not None]
    total = sum(weights[name] for name in available)
    return 100 * sum(weights[name] * parts[name] for name in available) / total


def score(
    links: list[dict],
    bugs: list[dict],
    executions: dict[tuple[str, str], dict],
    cycles: list[int],
    weights: dict,
) -> list[dict]:
    """Return one yield row per test, ranked overall and within its source.

    executions maps (source, test_key) to {"count", "cycles"}: valid executions
    and the release cycles they ran in. Without them F and R are missing and the
    other weights are scaled up to sum to 1, except in-tree tests, which run on
    every push and so are taken to have run in every cycle.
    """
    counted = {
        bug["bug_id"]: bug
        for bug in bugs
        if bug.get("type") == "defect" and bug.get("resolution") not in NOT_A_BUG
    }
    links = [
        link
        for link in links
        if link["test_key_type"] != "label" and link["bug_id"] in counted
    ]

    tests = defaultdict(lambda: {"bugs": set(), "results": set(), "case_id": None})
    for link in links:
        test = tests[(link["source"], link["test_key"])]
        test["bugs"].add(link["bug_id"])
        if link.get("result_id"):
            test["results"].add(link["result_id"])
        test["case_id"] = test["case_id"] or link.get("case_id")

    raw = {}
    for key, test in tests.items():
        found = [counted[bug_id] for bug_id in test["bugs"]]
        regression_cycles = {bug["cycle"] for bug in found if is_regression(bug)}
        executed = executions.get(key) or {}
        executed_cycles = executed.get("cycles") or (
            set(cycles) if key[0] == "in_tree" else set()
        )
        raw[key] = {
            # TestRail: results listing a bug. Summary links: the first failure
            # found the bug, so one per bug.
            "detections": len(test["results"]) or len(found),
            "executions": executed.get("count"),
            "executed_cycles": len(executed_cycles),
            "impact": sum(map(bug_impact, found)),
            "regression_cycles": len(regression_cycles),
        }

    # Each component is scaled against all tests in the period, whatever the source.
    components = {
        # log keeps one very productive test from flattening everyone else.
        "U": normalized(
            {k: len(test["bugs"]) for k, test in tests.items()}, math.log1p
        ),
        "F": {
            k: min(1.0, v["detections"] / v["executions"]) if v["executions"] else None
            for k, v in raw.items()
        },
        "S": normalized({k: v["impact"] for k, v in raw.items()}),
        "R": {
            k: min(1.0, v["regression_cycles"] / v["executed_cycles"])
            if v["executed_cycles"]
            else None
            for k, v in raw.items()
        },
    }
    rows = []
    for key, values in raw.items():
        parts = {name: components[name][key] for name in DEFAULT_WEIGHTS}
        rows.append(
            {
                "source": key[0],
                "test_key": key[1],
                "case_id": tests[key]["case_id"],
                "bugs_found": len(tests[key]["bugs"]),
                **values,
                **{f"{name.lower()}_score": part for name, part in parts.items()},
                "yield_score": yield_score(parts, weights),
                "missing_components": ",".join(
                    name for name, part in parts.items() if part is None
                )
                or None,
            }
        )

    rows.sort(key=lambda row: (-row["yield_score"], row["source"], row["test_key"]))
    in_source = Counter()
    for rank, row in enumerate(rows, 1):
        in_source[row["source"]] += 1
        row["rank"] = rank
        row["rank_in_source"] = in_source[row["source"]]
    return rows


def schema():
    from google.cloud import bigquery

    def field(name, field_type, mode="NULLABLE"):
        return bigquery.SchemaField(name, field_type, mode=mode)

    return [
        field("source", "STRING", "REQUIRED"),
        field("test_key", "STRING", "REQUIRED"),
        field("case_id", "INT64"),
        field("bugs_found", "INT64", "REQUIRED"),
        field("detections", "INT64"),
        field("executions", "INT64"),
        field("impact", "FLOAT64"),
        field("regression_cycles", "INT64"),
        field("executed_cycles", "INT64"),
        field("u_score", "FLOAT64"),
        field("f_score", "FLOAT64"),
        field("s_score", "FLOAT64"),
        field("r_score", "FLOAT64"),
        field("yield_score", "FLOAT64", "REQUIRED"),
        field("missing_components", "STRING"),
        field("rank", "INT64", "REQUIRED"),
        field("rank_in_source", "INT64", "REQUIRED"),
        field("weights", "STRING", "REQUIRED"),
        field("window_start", "DATE", "REQUIRED"),
        field("cycles", "STRING", "REQUIRED"),
        field("computed_at", "TIMESTAMP", "REQUIRED"),
    ]


def main() -> int:
    from google.cloud import bigquery

    project, dataset = os.environ["BQ_PROJECT"], os.environ["BQ_DATASET"]
    client = bigquery.Client(project=project)

    def read(query: str) -> list[dict]:
        job = client.query(
            query.replace("{dataset}", f"{project}.{dataset}"),
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("since", "DATE", SINCE_DATE)
                ]
            ),
        )
        return [dict(row) for row in job.result()]

    releases = release_dates()
    cycles = sorted(
        {
            cycle_of(date.fromisoformat(SINCE_DATE), releases),
            cycle_of(date.today(), releases),
        }
    )
    cycles = list(range(cycles[0], cycles[-1] + 1))
    bugs = read(f"SELECT * FROM `{{dataset}}.{BUGS_TABLE}`")

    daily = [
        ("testrail", f"C{row['case_id']}", row["executed_on"], row["executions"])
        for row in read(
            f"""
            SELECT case_id, executed_on, COUNT(*) AS executions
            FROM `{{dataset}}.{EXECUTIONS_TABLE}`
            GROUP BY case_id, executed_on
            """
        )
    ] + [
        ("starfox", row["test_key"], row["executed_on"], row["executions"])
        for row in read(
            f"""
            SELECT SPLIT(test_nodeid, '::')[OFFSET(0)] AS test_key,
                   DATE(run_started_at) AS executed_on,
                   COUNT(*) AS executions
            FROM `{{dataset}}.{STARFOX_RESULTS_TABLE}`
            WHERE DATE(run_started_at) >= @since
              AND outcome IN {STARFOX_EXECUTED}
            GROUP BY test_key, executed_on
            """
        )
    ]
    executions = defaultdict(lambda: {"count": 0, "cycles": set()})
    for source, test_key, executed_on, count in daily:
        executions[(source, test_key)]["count"] += count
        executions[(source, test_key)]["cycles"].add(cycle_of(executed_on, releases))
    for bug in bugs:
        bug["cycle"] = cycle_of(bug["creation_time"].date(), releases)

    used = weights()
    links = read(f"SELECT * FROM `{{dataset}}.{LINKS_TABLE}`")
    rows = score(links, bugs, executions, cycles, used)
    common = {
        "weights": ",".join(f"{name}={value}" for name, value in used.items())
        + f",severity={SEVERITY_WEIGHT}",
        "window_start": SINCE_DATE,
        "cycles": ",".join(map(str, cycles)),
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }
    client.load_table_from_json(
        [row | common for row in rows],
        f"{project}.{dataset}.{YIELD_TABLE}",
        job_config=bigquery.LoadJobConfig(
            schema=schema(),
            clustering_fields=["source", "rank"],
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        ),
    ).result()
    logging.info("Scored %d tests over cycles %s", len(rows), common["cycles"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
