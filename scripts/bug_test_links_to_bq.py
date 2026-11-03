"""
Load desktop Bugzilla bugs created since SINCE_DATE, and the tests that found them,
into BigQuery. A bug links to a test when its summary names an in-tree or STARfox
test, or when a TestRail result lists the bug in its Defects field.

Run with `uv run python -m scripts.bug_test_links_to_bq`. Each run reloads the
tables in full, so it is safe to re-run.
"""

import logging
import os
import re
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from time import sleep
from typing import Any, Iterator

import requests

from modules.testrail import APIError, TestRail
from modules.testrail_integration import PLAN_NAME_RE, TESTRAIL_FX_DESK_PRJ

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

SINCE_DATE = os.environ.get("SINCE_DATE") or "2026-10-13"
BUGZILLA_URL = "https://bugzilla.mozilla.org"
TREEHERDER_URL = "https://treeherder.mozilla.org/api/failuresbybug/"
HEADERS = {"User-Agent": "starfox-bug-test-links"}
BUGS_TABLE = "bugzilla_bugs"
LINKS_TABLE = "bug_test_links"
VIEW = "desktop_bugs_with_tests"

# Each query is one way a bug can be in scope; Unspecified bugs are kept only
# if Treeherder shows them failing on desktop.
SCOPE_QUERIES = [
    {"platform": "Desktop"},
    {"product": "Firefox", "platform": "All"},
    {"platform": "Unspecified", "keywords": "intermittent-failure"},
]
# Mozilla QA bugs are about fixing a STARfox test, not bugs a test found.
EXCLUDED_PRODUCTS = {"Mozilla QA"}
DESKTOP_OS = {"macOS", "Linux", "Unspecified", "All"}
DESKTOP_TREEHERDER_PLATFORMS = ("linux", "windows", "macosx")
BUG_FIELDS = [
    "id",
    "summary",
    "product",
    "component",
    "platform",
    "op_sys",
    "status",
    "resolution",
    "type",
    "severity",
    "priority",
    "keywords",
    "regressed_by",
    "groups",
    "creation_time",
    "last_change_time",
    # Bugzilla ignores fields that don't exist yet.
    *(f"cf_status_firefox{version}" for version in range(140, 200)),
]

TESTRAIL_PAGE = 250
BUGZILLA_PAGE = 500

# A test file path (forward or back slashes, WPT paths start with /), or a bare
# browser_*/test_* file name.
TEST_PATH_RE = re.compile(
    r"(?<![\w/\\.-])("
    r"/?(?:[\w.-]+[/\\])+[\w.-]+\.(?:js|mjs|sjs|html|xhtml|xht|xul|svg|py|toml|ini)"
    r"|(?:browser|test)_[\w.-]+\.(?:js|mjs|html|xhtml|py)"
    r")(?![\w/\\])"
)
# Leading words of a Treeherder-filed summary, e.g. "Intermittent [tier 2] TV".
SUMMARY_PREFIX_RE = re.compile(
    r"^(?:(?:Intermittent|Perma|Frequent|TV|TVW|TEST-UNEXPECTED-\w+|\[[^\]]*\])"
    r"\s*\|?\s+)+"
)
CASE_ID_RE = re.compile(r'def test_case\(\):\s*return "(\d+)"')
FX_VERSION_RE = re.compile(r"\d+\.\d+(?:b\d+|\.\d+)?(?:-build\d+)?")
BUG_ID_RE = re.compile(r"(?<![\w-])(\d{6,8})(?!\w)")


def since_epoch() -> int:
    return int(
        datetime.fromisoformat(SINCE_DATE).replace(tzinfo=timezone.utc).timestamp()
    )


def epoch_to_iso(value: int | None) -> str | None:
    return datetime.fromtimestamp(value, timezone.utc).isoformat() if value else None


def bug_ids(text: str | None) -> set[int]:
    return {int(match) for match in BUG_ID_RE.findall(text or "")}


def get_json(url: str, params: dict, retries: int = 5) -> Any:
    """GET with a wait-and-retry on rate limiting."""
    for attempt in range(retries):
        response = requests.get(url, params=params, headers=HEADERS, timeout=120)
        if response.status_code != 429 or attempt == retries - 1:
            response.raise_for_status()
            return response.json()
        sleep(int(response.headers.get("Retry-After", 60)))


# Bugzilla


def search_bugs() -> dict[int, dict]:
    """Return every public, non-QA, desktop-OS bug matched by a scope query."""
    params = {
        "creation_time": SINCE_DATE,
        "include_fields": ",".join(BUG_FIELDS),
        "order": "bug_id",
        "limit": BUGZILLA_PAGE,
    }
    if os.environ.get("BUGZILLA_API_KEY"):
        params["api_key"] = os.environ["BUGZILLA_API_KEY"]

    bugs = {}
    for query in SCOPE_QUERIES:
        offset = 0
        while True:
            page = get_json(
                f"{BUGZILLA_URL}/rest/bug", params | query | {"offset": offset}
            )["bugs"]
            for bug in page:
                bugs[bug["id"]] = bug
            if len(page) < BUGZILLA_PAGE:
                break
            offset += BUGZILLA_PAGE

    # Security bugs are left out until including them is approved.
    kept = {
        bug_id: bug
        for bug_id, bug in bugs.items()
        if not bug.get("groups")
        and bug["product"] not in EXCLUDED_PRODUCTS
        and (bug["op_sys"].startswith("Windows") or bug["op_sys"] in DESKTOP_OS)
    }
    logging.info("Bugzilla returned %d bugs, %d in scope", len(bugs), len(kept))
    return kept


def is_intermittent(bug: dict) -> bool:
    return "intermittent-failure" in bug["keywords"] or bug["summary"].startswith(
        ("Intermittent", "Perma")
    )


def desktop_failures(bug_id: int) -> Counter:
    """Count Treeherder failures per desktop platform, on Firefox (not comm-*) trees."""
    failures = get_json(
        TREEHERDER_URL,
        {
            "bug": bug_id,
            "startday": SINCE_DATE,
            "endday": date.today().isoformat(),
            "tree": "all",
        },
    )
    return Counter(
        failure["platform"]
        for failure in failures
        if failure["platform"].startswith(DESKTOP_TREEHERDER_PLATFORMS)
        and not failure["tree"].startswith("comm")
    )


def add_treeherder_failures(bugs: dict[int, dict]) -> dict[int, dict]:
    """Add desktop failure counts to intermittents; drop Unspecified ones with none."""
    intermittents = [bug for bug in bugs.values() if is_intermittent(bug)]
    logging.info("Checking %d intermittent bugs on Treeherder", len(intermittents))
    for bug in intermittents:
        bug["desktop_failures"] = desktop_failures(bug["id"])
    return {
        bug_id: bug
        for bug_id, bug in bugs.items()
        if bug["platform"] != "Unspecified" or bug.get("desktop_failures")
    }


# Summary matching


def starfox_tests(root: Path = Path("tests")) -> dict[str, dict]:
    """Map each STARfox test file stem and test function name to its file and case."""
    tests = {}
    for path in sorted(root.rglob("test_*.py")):
        text = path.read_text(encoding="utf-8")
        case_id = CASE_ID_RE.search(text)
        test = {
            "path": path.as_posix(),
            "case_id": int(case_id.group(1)) if case_id else None,
        }
        tests[path.stem] = test
        for name in re.findall(r"^def (test_\w+)\(", text, re.MULTILINE):
            tests.setdefault(name, test)
    return tests


def starfox_name_re(tests: dict[str, dict]) -> re.Pattern:
    """Match a STARfox name as a whole token, not as the start of e.g. test_x.js."""
    names = "|".join(sorted(map(re.escape, tests), key=len, reverse=True))
    return re.compile(rf"(?<![\w/\\.])({names})(?:\.py)?(?!\w|\.\w|[/\\])")


def summary_links(bug: dict, tests: dict[str, dict], name_re: re.Pattern) -> list:
    """Return in-tree and STARfox tests named in a bug summary."""
    summary = bug["summary"]
    links = {}
    for match in TEST_PATH_RE.findall(summary):
        path = match.replace("\\", "/")
        test = tests.get(Path(path).stem)
        if test and test["path"].endswith(path):
            links[test["path"]] = ("starfox", "path", test["case_id"])
        else:
            links[path] = ("in_tree", "path", None)

    for name in name_re.findall(summary):
        test = tests[name]
        links.setdefault(test["path"], ("starfox", "path", test["case_id"]))

    # An intermittent naming no test file, e.g. "Intermittent leakcheck | ...";
    # often a harness check or an infra failure rather than one test.
    if not links and is_intermittent(bug):
        label = SUMMARY_PREFIX_RE.sub("", summary).split(" | ")[0].strip()
        if label:
            # A path with no file name, e.g. a tracking bug for browser_foo_*.
            key_type = "path" if "/" in label and " " not in label else "label"
            links[label] = ("in_tree", key_type, None)

    return [
        {
            "bug_id": bug["id"],
            "source": source,
            "test_key": key,
            "test_key_type": key_type,
            "case_id": case_id,
        }
        for key, (source, key_type, case_id) in links.items()
    ]


# TestRail


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


def runs_since(reader: TestRailReader, milestones: dict[int, dict]) -> Iterator:
    """Yield every run created since SINCE_DATE, in a plan or standalone, with context."""
    created_after = since_epoch()
    for plan in reader.paged(
        f"get_plans/{TESTRAIL_FX_DESK_PRJ}&created_after={created_after}", "plans"
    ):
        plan_channel = PLAN_NAME_RE.match(plan["name"] or "")
        context = {
            "plan_id": plan["id"],
            "plan_name": plan["name"],
            "channel": plan_channel.group(1) if plan_channel else None,
            **milestone_context(milestones, plan.get("milestone_id")),
        }
        for entry in reader.get(f"get_plan/{plan['id']}").get("entries", []):
            for run in entry.get("runs", []):
                yield run | {"entry_name": entry["name"]}, context

    for run in reader.paged(
        f"get_runs/{TESTRAIL_FX_DESK_PRJ}&created_after={created_after}", "runs"
    ):
        yield (
            run | {"entry_name": None},
            {
                "plan_id": None,
                "plan_name": None,
                "channel": None,
                **milestone_context(milestones, run.get("milestone_id")),
            },
        )


def testrail_links(reader: TestRailReader) -> list[dict]:
    """One link per bug in a result's Defects, with its run's release context."""
    milestones = reader.milestones()
    statuses = reader.statuses()
    links = []
    for run, context in runs_since(reader, milestones):
        results = [
            result
            for result in reader.paged(f"get_results_for_run/{run['id']}", "results")
            if bug_ids(result.get("defects"))
        ]
        if not results:
            continue

        tests = {
            test["id"]: test for test in reader.paged(f"get_tests/{run['id']}", "tests")
        }
        fx_version = FX_VERSION_RE.search(run["name"] or "")
        for result in results:
            test = tests.get(result["test_id"], {})
            for bug_id in bug_ids(result["defects"]):
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
                        "result_status": statuses.get(result.get("status_id")),
                        "result_created_at": epoch_to_iso(result.get("created_on")),
                    }
                )
    logging.info("Found %d TestRail result links", len(links))
    return links


# BigQuery


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
    return bugs, links


def replace_table(client, table_id: str, rows: list[dict], schema, clustering):
    from google.cloud import bigquery

    client.load_table_from_json(
        rows,
        table_id,
        job_config=bigquery.LoadJobConfig(
            schema=schema,
            clustering_fields=clustering,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        ),
    ).result()
    logging.info("Loaded %d rows into %s", len(rows), table_id)


def collect() -> tuple[list[dict], list[dict]]:
    """Return the in-scope bugs that link to a test, and those links."""
    bugs = add_treeherder_failures(search_bugs())

    tests = starfox_tests()
    name_re = starfox_name_re(tests)
    links = [
        link for bug in bugs.values() for link in summary_links(bug, tests, name_re)
    ]
    links += [
        link for link in testrail_links(TestRailReader()) if link["bug_id"] in bugs
    ]

    linked = {link["bug_id"] for link in links}
    logging.info(
        "%d bugs link to a test: %s",
        len(linked),
        dict(Counter(link["source"] for link in links)),
    )
    return [bugs[bug_id] for bug_id in sorted(linked)], links


def main() -> int:
    from google.cloud import bigquery

    project, dataset = os.environ["BQ_PROJECT"], os.environ["BQ_DATASET"]
    ingested_at = datetime.now(timezone.utc).isoformat()
    bugs, links = collect()

    bugs_schema, links_schema = schemas()
    client = bigquery.Client(project=project)
    replace_table(
        client,
        f"{project}.{dataset}.{BUGS_TABLE}",
        [bug_row(bug, ingested_at) for bug in bugs],
        bugs_schema,
        ["product", "component"],
    )
    replace_table(
        client,
        f"{project}.{dataset}.{LINKS_TABLE}",
        [link | {"ingested_at": ingested_at} for link in links],
        links_schema,
        ["source", "test_key"],
    )
    client.query(
        f"""
        CREATE OR REPLACE VIEW `{project}.{dataset}.{VIEW}` AS
        SELECT bug.* EXCEPT (ingested_at), link.* EXCEPT (bug_id, ingested_at)
        FROM `{project}.{dataset}.{BUGS_TABLE}` AS bug
        JOIN `{project}.{dataset}.{LINKS_TABLE}` AS link USING (bug_id)
        """
    ).result()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
