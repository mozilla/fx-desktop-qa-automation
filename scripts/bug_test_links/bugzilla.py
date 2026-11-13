"""Find in-scope Bugzilla bugs, and confirm Unspecified ones on Treeherder."""

import logging
import os
from collections import Counter
from datetime import date

from scripts.bug_test_links.common import SINCE_DATE, get_json

BUGZILLA_URL = "https://bugzilla.mozilla.org"
TREEHERDER_URL = "https://treeherder.mozilla.org/api/failuresbybug/"
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
BUGZILLA_PAGE = 500


def bugzilla_params() -> dict:
    params = {"include_fields": ",".join(BUG_FIELDS)}
    if os.environ.get("BUGZILLA_API_KEY"):
        params["api_key"] = os.environ["BUGZILLA_API_KEY"]
    return params


def search_bugs(changed_since: str | None = None) -> dict[int, dict]:
    """Return every bug created since SINCE_DATE (and, if given, changed since
    changed_since) matched by a scope query, in scope or not."""
    params = bugzilla_params() | {
        "creation_time": SINCE_DATE,
        "order": "bug_id",
        "limit": BUGZILLA_PAGE,
    }
    if changed_since:
        params["last_change_time"] = changed_since

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
    logging.info("Bugzilla search returned %d bugs", len(bugs))
    return bugs


def fetch_bugs(ids: set[int]) -> dict[int, dict]:
    """Return the given bugs that are public, so visible to Bugzilla's API."""
    ordered = sorted(ids)
    bugs = {}
    for start in range(0, len(ordered), 200):
        batch = ",".join(map(str, ordered[start : start + 200]))
        for bug in get_json(
            f"{BUGZILLA_URL}/rest/bug", bugzilla_params() | {"id": batch}
        )["bugs"]:
            bugs[bug["id"]] = bug
    return bugs


def in_scope(bug: dict) -> bool:
    """Apply the scope rules, except the Treeherder check on Unspecified bugs."""
    platform, product = bug["platform"], bug["product"]
    # Security bugs are left out until including them is approved.
    return (
        not bug.get("groups")
        and bug["creation_time"] >= SINCE_DATE
        and product not in EXCLUDED_PRODUCTS
        and (bug["op_sys"].startswith("Windows") or bug["op_sys"] in DESKTOP_OS)
        and (
            platform == "Desktop"
            or (platform == "All" and product == "Firefox")
            or (platform == "Unspecified" and is_intermittent(bug))
        )
    )


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
