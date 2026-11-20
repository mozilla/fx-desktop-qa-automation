"""
Score each test's yield from the bug_test_links and bugzilla_bugs tables and
write it to the test_yield table:

    Yield = 100 * (wU*U + wF*F + wS*S + wR*R)

Coverage (C) is left out until its inputs exist, and its weight shared equally.
"""

import logging
import math
import os
import tomllib
from bisect import bisect_right
from collections import Counter, defaultdict
from collections.abc import Callable
from datetime import date, datetime, timezone
from pathlib import Path

import requests

from scripts.bug_test_links.common import SINCE_DATE
from scripts.bug_test_links.release_check import major_releases
from scripts.bug_test_links.summary import starfox_tests
from scripts.bug_test_links.tables import BUGS_TABLE, EXECUTIONS_TABLE, LINKS_TABLE

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

STARFOX_RESULTS_TABLE = "test_results"
YIELD_TABLE = "test_yield"
VERSIONS_URL = "https://product-details.mozilla.org/1.0/firefox_versions.json"

CONFIG_FILE = Path(__file__).parent / "bug_test_links" / "yield_config.toml"
COMPONENTS = ("U", "F", "S", "R")
# Resolutions meaning the report wasn't a new, real bug.
NOT_A_BUG = {"INVALID", "WORKSFORME", "INCOMPLETE", "DUPLICATE"}
# STARfox CI outcomes where the test ran to a verdict; rerun is fail-then-pass.
STARFOX_EXECUTED = ("passed", "failed", "rerun")


def checked_weights(parsed: dict[str, float], source: str) -> dict[str, float]:
    """Return parsed if it has positive U, F, S and R summing to 1, else exit."""
    if (
        set(parsed) != set(COMPONENTS)
        or min(parsed.values()) <= 0
        or not math.isclose(sum(parsed.values()), 1.0)
    ):
        raise SystemExit(f"{source} needs positive U, F, S and R summing to 1")
    return parsed


def checked_share(value: float, source: str) -> float:
    """Return value if it is between 0 and 1, else exit."""
    if not 0 <= value <= 1:
        raise SystemExit(f"{source} must be between 0 and 1, not {value}")
    return value


def load_config(path: Path = CONFIG_FILE) -> dict:
    """Read the weights and impact scales, applying the YIELD_* overrides."""
    config = tomllib.loads(path.read_text(encoding="utf-8"))
    impact = config["impact"]
    raw_weights = os.environ.get("YIELD_WEIGHTS")
    if raw_weights:
        weights = {
            key.strip(): float(value)
            for key, value in (part.split("=") for part in raw_weights.split(","))
        }
        weights = checked_weights(weights, "YIELD_WEIGHTS")
    else:
        weights = checked_weights(config["weights"], path.name)
    raw_share = os.environ.get("YIELD_SEVERITY_WEIGHT")
    severity_weight = (
        checked_share(float(raw_share), "YIELD_SEVERITY_WEIGHT")
        if raw_share
        else checked_share(impact["severity_weight"], path.name)
    )
    for scale in ("severity", "priority"):
        for level, value in impact[scale].items():
            checked_share(value, f"{path.name} {scale} {level}")
    return {
        "weights": weights,
        "severity_weight": severity_weight,
        "severity": impact["severity"],
        "priority": impact["priority"],
    }


CONFIG = load_config()


def release_dates() -> list[tuple[date, int]]:
    """Return (release date, major version) for every release, next one included."""
    releases = major_releases()
    upcoming = requests.get(VERSIONS_URL, timeout=60).json()["NEXT_RELEASE_DATE"]
    latest = max(version for _, version in releases)
    return releases + [(date.fromisoformat(upcoming), latest + 1)]


def cycle_of(day: date, releases: list[tuple[date, int]]) -> int:
    """Return the version that ships at the end of the cycle containing day."""
    index = bisect_right([released for released, _ in releases], day)
    if index == len(releases):
        return releases[-1][1] + 1
    return releases[index][1]


def bug_impact(bug: dict) -> float:
    """Weighted severity and priority on a 0-1 scale; unset counts as 0."""
    share = CONFIG["severity_weight"]
    return share * CONFIG["severity"].get(bug.get("severity"), 0.0) + (
        1 - share
    ) * CONFIG["priority"].get(bug.get("priority"), 0.0)


def automated_cases() -> dict[int, str]:
    """Map each TestRail case that a STARfox test automates to that test's file."""
    return {
        test["case_id"]: test["path"]
        for test in starfox_tests().values()
        if test["case_id"]
    }


def merge_automated_executions(
    executions: dict[tuple[str, str], dict], automated: dict[int, str]
) -> None:
    """Count an automated case's executions once, under its STARfox test.

    STARfox CI reports its runs to TestRail, so TestRail's results for the case
    are the same runs; they're used only when CI has none.

    Parameters
    ----------
    executions
        (source, test_key) -> {"count": valid executions, "cycles": release
        cycles run in}; changed in place.
    automated
        TestRail case ID -> path of the STARfox test that automates it.
    """
    for case_id, path in automated.items():
        reported = executions.pop(("testrail", f"C{case_id}"), None)
        if not reported:
            continue
        ci = executions.get(("starfox", path))
        if ci:
            ci["cycles"] |= reported["cycles"]
        else:
            executions[("starfox", path)] = reported


def is_regression(bug: dict) -> bool:
    return "regression" in (bug.get("keywords") or []) or bool(bug.get("regressed_by"))


def normalized(
    values: dict, scale: Callable[[float], float] = lambda value: value
) -> dict:
    """Divide each value by the largest one; all zeros stay zero.

    Parameters
    ----------
    values
        Test key -> raw value.
    scale
        Applied to every value before dividing, e.g. math.log1p for U.
    """
    top = max((scale(value) for value in values.values()), default=0)
    return {key: scale(value) / top if top else 0.0 for key, value in values.items()}


def yield_score(parts: dict[str, float | None], weights: dict[str, float]) -> float:
    """Return 100 * the weighted sum of a test's components.

    Parameters
    ----------
    parts
        Component name ("U", "F", "S", "R") -> score from 0 to 1, or None if the
        test has no data for it; the other weights are then scaled up to sum to 1.
    weights
        Component name -> weight; the weights sum to 1.
    """
    available = [name for name, part in parts.items() if part is not None]
    total = sum(weights[name] for name in available)
    return 100 * sum(weights[name] * parts[name] for name in available) / total


def score(
    links: list[dict],
    bugs: list[dict],
    executions: dict[tuple[str, str], dict],
    cycles: list[int],
    weights: dict,
    automated: dict[int, str] | None = None,
) -> list[dict]:
    """Return one yield row per test, ranked overall and within its source.

    Parameters
    ----------
    links
        Rows of the bug_test_links table.
    bugs
        Rows of the bugzilla_bugs table, each with the release "cycle" it was
        filed in.
    executions
        (source, test_key) -> {"count": valid executions, "cycles": release
        cycles run in}. A test without an entry has no F or R, except in-tree
        tests, which run on every push and so count as run in every cycle.
    cycles
        Release cycles in the analysis period, e.g. [159, 160].
    weights
        Component name ("U", "F", "S", "R") -> weight; the weights sum to 1.
    automated
        TestRail case ID -> path of the STARfox test that automates it; the
        case and that test are scored as one test.
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

    # A bug linked to several tests counts in full for each of them.
    automated = automated or {}
    tests = defaultdict(
        lambda: {"bugs": set(), "results": set(), "result_bugs": set(), "case_id": None}
    )
    for link in links:
        case_id = link.get("case_id")
        key = (
            ("starfox", automated[case_id])
            if case_id in automated
            else (link["source"], link["test_key"])
        )
        test = tests[key]
        test["bugs"].add(link["bug_id"])
        if link.get("result_id"):
            test["results"].add(link["result_id"])
            test["result_bugs"].add(link["bug_id"])
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
            # TestRail results that list a bug, plus one per bug named only in a
            # summary, whose first failure found it.
            "detections": len(test["results"])
            + len(test["bugs"] - test["result_bugs"]),
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
        parts = {name: components[name][key] for name in COMPONENTS}
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
    first = cycle_of(date.fromisoformat(SINCE_DATE), releases)
    last = cycle_of(date.today(), releases)
    cycles = list(range(first, last + 1))
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

    used = CONFIG["weights"]
    links = read(f"SELECT * FROM `{{dataset}}.{LINKS_TABLE}`")
    automated = automated_cases()
    merge_automated_executions(executions, automated)
    rows = score(links, bugs, executions, cycles, used, automated)
    common = {
        "weights": ",".join(f"{name}={value}" for name, value in used.items())
        + f",severity={CONFIG['severity_weight']}",
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
