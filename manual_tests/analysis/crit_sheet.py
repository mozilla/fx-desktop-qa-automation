"""Worksheet dumper for the critical round.

python crit_sheet.py                 # population overview, per suite
python crit_sheet.py 69142           # every critical case in that suite, by section
python crit_sheet.py 69142 --steps   # ... with the first few manual steps inlined
python crit_sheet.py --todo          # suites still missing verdicts, worst first
"""

import collections
import glob
import importlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import _ledger  # noqa: E402
import crit_pop  # noqa: E402


def load_verdicts():
    """{case_id: (tier, cluster)} from this round's c_*.py files only."""
    _ledger.CLUSTERS.clear()
    for f in sorted(glob.glob(os.path.join(HERE, "c_*.py"))):
        mod = os.path.basename(f)[:-3]
        if mod in ("crit_pop", "crit_sheet"):
            continue
        importlib.import_module(mod)
    out = {}
    for cl in _ledger.CLUSTERS:
        for cid in cl["ids"]:
            out[cid] = (cl["tier"], cl)
    return out


def clean(s):
    if not s:
        return ""
    s = re.sub(r"!?\[[^\]]*\]\([^)]*\)", "", s)  # images / links
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def main():
    args = [a for a in sys.argv[1:]]
    steps = "--steps" in args
    todo = "--todo" in args
    args = [a for a in args if not a.startswith("--")]

    pop = crit_pop.population()
    verdicts = load_verdicts()

    if not args:
        rows = collections.Counter(c["suite_id"] for c in pop.values())
        done = collections.Counter(pop[i]["suite_id"] for i in pop if i in verdicts)
        print(
            "Critical + not-Automation-Completed: %d cases, %d suites\n"
            % (len(pop), len(rows))
        )
        print("%-8s %-46s %6s %6s" % ("suite", "name", "cases", "done"))
        for s, n in rows.most_common():
            if todo and done.get(s, 0) >= n:
                continue
            print(
                "%-8s %-46s %6d %6d"
                % (s, crit_pop.SUITE_NAMES.get(s, "?")[:46], n, done.get(s, 0))
            )
        print(
            "\ntotal %d, with a verdict %d, remaining %d"
            % (
                len(pop),
                len(verdicts.keys() & pop.keys()),
                len(pop) - len(verdicts.keys() & pop.keys()),
            )
        )
        return

    suite = int(args[0])
    cs = [c for c in pop.values() if c["suite_id"] == suite]
    bysec = collections.defaultdict(list)
    for c in cs:
        bysec[c["section_id"]].append(c)
    print(
        "=== suite %s  %s  -- %d critical/non-automated cases, %d sections"
        % (suite, crit_pop.SUITE_NAMES.get(suite, "?"), len(cs), len(bysec))
    )
    for sec in sorted(bysec, key=lambda s: -len(bysec[s])):
        print("\n-- section %s  (%d)" % (sec, len(bysec[sec])))
        for c in sorted(bysec[sec], key=lambda c: c["id"]):
            mark = verdicts[c["id"]][0][:4] if c["id"] in verdicts else "    "
            print("  %s %-9s %s" % (mark, c["id"], clean(c["title"])[:105]))
            if steps:
                body = clean(c.get("custom_steps") or "")
                if not body and c.get("custom_steps_separated"):
                    body = " | ".join(
                        clean(s.get("content", ""))
                        for s in c["custom_steps_separated"][:4]
                    )
                if body:
                    print("            %s" % body[:300])


main()
