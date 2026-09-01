"""Round 5 population -- STARfox-automated cases, and the STARfox tests behind them.

Selection: any priority, and `custom_automation_coverage` in (2, 3) -- the TestRail field
that records a case as covered by STARfox automation.

Unlike rounds 1-4, the unit of analysis here is not the manual case but the **STARfox test
file**. Most cases carry a `custom_automated_test_names` field naming the test that covers
them, so the question this round asks is:

    for each automated STARfox test, does mozilla-firefox/firefox already have a test that
    drives the same flow and asserts the same outcome?

That is a sharper comparison than rounds 1-4 could make, because both sides are real code:
the STARfox test is in this repo and can be read directly.
"""

import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

_CASES = None


def cases():
    global _CASES
    if _CASES is None:
        p = os.path.join(ROOT, "manual_tests", "all_cases.json")
        if not os.path.exists(p):
            raise SystemExit(
                "manual_tests/all_cases.json is missing (gitignored, ~30MB). "
                "Re-export the TestRail corpus; see manual_tests/analysis/README.md."
            )
        _CASES = json.load(open(p, encoding="utf-8"))
    return _CASES


def by_id():
    out = {}
    for c in cases():
        out.setdefault(c["id"], c)  # a few ids are duplicated rows in the export
    return out


def population():
    """{case_id: case} for every case marked as covered by STARfox automation."""
    return {
        cid: c
        for cid, c in by_id().items()
        if c.get("custom_automation_coverage") in (2, 3)
    }


_REPO_TESTS = None


def repo_tests():
    """Every STARfox test file currently in the tree, as repo-relative posix paths."""
    global _REPO_TESTS
    if _REPO_TESTS is None:
        found = glob.glob(os.path.join(ROOT, "tests", "**", "*.py"), recursive=True)
        _REPO_TESTS = {
            os.path.relpath(p, ROOT).replace(os.sep, "/")
            for p in found
            if os.path.basename(p).startswith("test_")
        }
    return _REPO_TESTS


def parse_test_names(raw):
    """TestRail stores the field as a small HTML blob, sometimes with several paths."""
    if not raw:
        return []
    text = re.sub(r"<[^>]+>", " ", raw)
    return [t.strip() for t in re.split(r"[\s,;]+", text) if t.strip().endswith(".py")]


def resolve(name):
    """Map a cited test name onto a file that exists, or None.

    TestRail entries are inconsistent: some are repo-relative ("tests/tabs/test_x.py"),
    some omit the leading "tests/", some name a path that has since been renamed.
    """
    tests = repo_tests()
    if name in tests:
        return name
    alt = "tests/" + name.lstrip("/")
    if alt in tests:
        return alt
    base = os.path.basename(name)
    matches = [p for p in tests if os.path.basename(p) == base]
    return matches[0] if len(matches) == 1 else None


def links():
    """(by_test, unlinked, dead) for the population.

    by_test  {starfox_test_path: [case_id, ...]}
    unlinked [case_id, ...]          - marked covered, but no test name recorded
    dead     {cited_name: [case_id]} - names a STARfox test that no longer exists
    """
    by_test = {}
    unlinked = []
    dead = {}
    for cid, c in sorted(population().items()):
        names = parse_test_names(c.get("custom_automated_test_names"))
        if not names:
            unlinked.append(cid)
            continue
        hit = False
        for n in names:
            p = resolve(n)
            if p:
                by_test.setdefault(p, []).append(cid)
                hit = True
            else:
                dead.setdefault(n, []).append(cid)
        if not hit:
            unlinked.append(cid)
    return by_test, unlinked, dead
