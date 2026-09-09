"""Worksheet dumper for round 5.

python sheet.py                       # overview: STARfox suite dirs, linked vs done
python sheet.py tests/tabs            # every linked test in that dir, with its cases
python sheet.py tests/tabs --titles   # ... with the TestRail case titles
python sheet.py --todo                # only dirs with unassessed tests
python sheet.py --orphans             # linked-but-missing, and covered-but-unlinked
"""

import collections
import glob
import importlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ledger  # noqa: E402
import pop  # noqa: E402


def load_verdicts():
    ledger.CLUSTERS.clear()
    for f in sorted(glob.glob(os.path.join(HERE, "a_*.py"))):
        importlib.import_module(os.path.basename(f)[:-3])
    return {s: cl for cl in ledger.CLUSTERS for s in cl["starfox"]}


def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


def main():
    args = sys.argv[1:]
    titles = "--titles" in args
    todo = "--todo" in args
    orphans = "--orphans" in args
    args = [a for a in args if not a.startswith("--")]

    by_test, unlinked, dead = pop.links()
    verdicts = load_verdicts()
    cases = pop.by_id()

    if orphans:
        print("STARfox tests named in TestRail that no longer exist (%d):" % len(dead))
        for name in sorted(dead):
            ids = ", ".join("C%d" % i for i in dead[name])
            print("  %-78s  %s" % (name, ids))
        print()
        print("Cases marked covered but with no usable test name (%d):" % len(unlinked))
        for cid in unlinked[:40]:
            print("  C%-9s %s" % (cid, clean(cases[cid]["title"])[:88]))
        if len(unlinked) > 40:
            print("  ... %d more" % (len(unlinked) - 40))
        print()
        linked = set(by_test)
        untouched = sorted(pop.repo_tests() - linked)
        print(
            "STARfox tests with no TestRail case pointing at them (%d):"
            % len(untouched)
        )
        for p in untouched[:40]:
            print("  %s" % p)
        if len(untouched) > 40:
            print("  ... %d more" % (len(untouched) - 40))
        return

    if not args:
        dirs = collections.Counter(os.path.dirname(p) for p in by_test)
        done = collections.Counter(os.path.dirname(p) for p in by_test if p in verdicts)
        print(
            "STARfox-automated cases: %d, linked to %d distinct tests\n"
            % (len(pop.population()), len(by_test))
        )
        print("%-42s %7s %6s" % ("STARfox suite dir", "tests", "done"))
        for d, n in dirs.most_common():
            if todo and done.get(d, 0) >= n:
                continue
            print("%-42s %7d %6d" % (d, n, done.get(d, 0)))
        print(
            "\ntotal tests %d, with a verdict %d, remaining %d"
            % (
                len(by_test),
                len(verdicts.keys() & by_test.keys()),
                len(by_test) - len(verdicts.keys() & by_test.keys()),
            )
        )
        return

    d = args[0].rstrip("/")
    hit = sorted(p for p in by_test if os.path.dirname(p) == d)
    print("=== %s -- %d linked tests" % (d, len(hit)))
    for p in hit:
        mark = verdicts[p]["tier"][:4] if p in verdicts else "    "
        ids = ", ".join("C%d" % i for i in by_test[p])
        print("  %s %-58s %s" % (mark, os.path.basename(p), ids))
        if titles:
            for cid in by_test[p]:
                print("           C%-9s %s" % (cid, clean(cases[cid]["title"])[:84]))


main()
