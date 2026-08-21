"""Helpers for the critical round.

Several suites in this population are repetition matrices: the same handful of flows
re-stated once per platform, per theme or per entry point, under identical titles. Listing
their case ids by hand invites transcription errors, so CT() resolves a cluster from the
case *titles* instead.
"""

import re
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from _ledger import C  # noqa: E402
import crit_pop  # noqa: E402

_POP = None


def _pop():
    global _POP
    if _POP is None:
        _POP = crit_pop.population()
    return _POP


def _norm(s):
    return re.sub(r"\s+", " ", s or "").strip().lower()


def CT(suite, tier, tests, why, titles):
    """Cluster every case in `suite` whose title matches one of `titles` (case- and
    whitespace-insensitive, exact match after normalisation)."""
    want = {_norm(t) for t in titles}
    ids = [
        c["id"]
        for c in _pop().values()
        if c["suite_id"] == suite and _norm(c["title"]) in want
    ]
    seen = {_norm(c["title"]) for c in _pop().values() if c["suite_id"] == suite}
    for t in sorted(want - seen):
        raise SystemExit("CT(%s): no case titled %r" % (suite, t))
    C(suite, tier, tests, why, ids)


def CREST(suite, tier, tests, why):
    """Cluster every case in `suite` not already claimed by an earlier cluster.

    Used for suites where a single rationale covers the whole remainder (live-site sweeps,
    visual-rendering sweeps, installer matrices). Must be called after that suite's other
    clusters -- files load in filename order, and calls run top to bottom within a file.
    """
    import _ledger

    claimed = {cid for cl in _ledger.CLUSTERS for cid in cl["ids"]}
    ids = [
        c["id"]
        for c in _pop().values()
        if c["suite_id"] == suite and c["id"] not in claimed
    ]
    if not ids:
        raise SystemExit("CREST(%s): nothing left unclaimed" % suite)
    C(suite, tier, tests, why, ids)


def CTP(suite, tier, tests, why, patterns):
    """Same as CT() but each entry is a regex matched against the normalised title."""
    rx = [re.compile(p, re.I) for p in patterns]
    ids = [
        c["id"]
        for c in _pop().values()
        if c["suite_id"] == suite and any(r.search(_norm(c["title"])) for r in rx)
    ]
    if not ids:
        raise SystemExit("CTP(%s): no cases matched %r" % (suite, patterns))
    C(suite, tier, tests, why, ids)
