"""Shared collector for the per-suite verdict files (d_*.py)."""

import json
import os

CLUSTERS = []

_CASES = None


def cases():
    global _CASES
    if _CASES is None:
        p = os.path.join(os.path.dirname(__file__), "..", "all_cases.json")
        if not os.path.exists(p):
            raise SystemExit(
                "manual_tests/all_cases.json is missing (it is gitignored - ~30MB). "
                "Re-export the TestRail case corpus; see manual_tests/analysis/README.md."
            )
        _CASES = json.load(open(p, encoding="utf-8"))
    return _CASES


def C(suite, tier, tests, why, ids):
    CLUSTERS.append(
        {"suite": suite, "tier": tier, "tests": tests, "why": why, "ids": list(ids)}
    )


def CSEC(suite, tier, tests, why, section_ids, exclude=()):
    """Same as C() but takes whole TestRail section ids instead of case ids.

    Used where a manual section is a repetition matrix (e.g. 'add .<ext> to Firefox'
    x 110 extensions) and every row maps to the same in-tree mechanic.
    """
    sections = set(section_ids)
    skip = set(exclude)
    ids = [
        c["id"]
        for c in cases()
        if c["suite_id"] == suite and c["section_id"] in sections and c["id"] not in skip
    ]
    C(suite, tier, tests, why, ids)
