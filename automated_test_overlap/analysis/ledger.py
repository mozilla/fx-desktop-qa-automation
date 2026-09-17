"""Shared collector for the round-5 verdict files (a_*.py).

A cluster is keyed by STARfox test path rather than by TestRail case id: the question is
whether a given automated STARfox test duplicates work already done in
mozilla-firefox/firefox. build_report.py joins the clusters back onto the TestRail cases
through pop.links().
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pop  # noqa: E402

CLUSTERS = []

TIERS = ("STRONG", "PARTIAL", "UNIQUE")
#   STRONG   an in-tree test drives the same flow and asserts the same outcome. The STARfox
#            test is redundant with the tree.
#   PARTIAL  the tree covers part of it -- a narrower scope, one variant, the component but
#            not the integration -- so the STARfox test still earns its place.
#   UNIQUE   nothing in the tree covers this. STARfox is the only automated coverage.


def T(tier, tests, why, starfox, area=None):
    """Record a verdict for one or more STARfox test files.

    tests    in-tree test paths backing the verdict ("n/a" for UNIQUE)
    why      the rationale, in prose
    starfox  STARfox test path(s) this applies to
    area     optional grouping label; defaults to the STARfox suite directory
    """
    if isinstance(starfox, str):
        starfox = [starfox]
    known = pop.repo_tests()
    for s in starfox:
        if s not in known:
            raise SystemExit("T(): no such STARfox test in the repo: %r" % s)
    CLUSTERS.append(
        {
            "tier": tier,
            "tests": tests,
            "why": why,
            "starfox": list(starfox),
            "area": area or os.path.dirname(starfox[0]),
        }
    )


def TDIR(tier, tests, why, directory, exclude=()):
    """Same as T() but takes every linked STARfox test in a directory.

    Used where a whole STARfox suite folder maps onto one in-tree directory.
    """
    by_test, _, _ = pop.links()
    skip = set(exclude)
    hit = [
        p
        for p in sorted(by_test)
        if os.path.dirname(p) == directory.rstrip("/") and p not in skip
    ]
    if not hit:
        raise SystemExit("TDIR(): nothing linked under %r" % directory)
    T(tier, tests, why, hit, area=directory.rstrip("/"))


def TREST(tier, tests, why, directory):
    """Cluster the linked STARfox tests in a directory that no earlier cluster claimed."""
    by_test, _, _ = pop.links()
    claimed = {s for cl in CLUSTERS for s in cl["starfox"]}
    hit = [
        p
        for p in sorted(by_test)
        if os.path.dirname(p) == directory.rstrip("/") and p not in claimed
    ]
    if not hit:
        raise SystemExit("TREST(): nothing left unclaimed under %r" % directory)
    T(tier, tests, why, hit, area=directory.rstrip("/"))
