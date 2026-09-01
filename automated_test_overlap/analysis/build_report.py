"""Build the round-5 report: automated STARfox tests vs the Firefox tree.

Population: TestRail cases with custom_automation_coverage in (2, 3) -- i.e. recorded as
covered by STARfox automation -- at any priority.

Outputs, all under automated_test_overlap/:
  STARFOX_TREE_OVERLAP.csv        one row per STARfox test, with the cases it covers
  STARFOX_TREE_OVERLAP_cases.csv  one row per TestRail case, for TestRail-side filtering
  analysis/summary.md             per-suite tables
  analysis/housekeeping.md        dead links, unlinked cases, untested STARfox files

Cases are named the way TestRail names them: "C" + the export's id, e.g. C2241112.
"""

import collections
import csv
import glob
import importlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import ledger  # noqa: E402
import pop  # noqa: E402

for f in sorted(glob.glob(os.path.join(HERE, "a_*.py"))):
    importlib.import_module(os.path.basename(f)[:-3])

PRIORITY = {1: "Low", 2: "Medium", 3: "High", 4: "Critical"}
COVERAGE = {2: "Partial", 3: "Full"}


def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


def main():
    by_test, unlinked, dead = pop.links()
    cases = pop.by_id()
    verdict = {s: cl for cl in ledger.CLUSTERS for s in cl["starfox"]}

    dupes = collections.Counter(s for cl in ledger.CLUSTERS for s in cl["starfox"])
    dupes = {k: v for k, v in dupes.items() if v > 1}
    missing = sorted(set(by_test) - set(verdict))

    # ---- one row per STARfox test
    rows = []
    for s in sorted(by_test):
        cl = verdict.get(s)
        if not cl:
            continue
        ids = sorted(by_test[s])
        rows.append(
            {
                "starfox_test": s,
                "starfox_suite": os.path.dirname(s),
                "verdict": cl["tier"],
                "testrail_cases": " ".join("C%d" % i for i in ids),
                "case_count": len(ids),
                "in_tree_tests": clean(cl["tests"]),
                "why": clean(cl["why"]),
            }
        )
    out1 = os.path.join(OUT, "STARFOX_TREE_OVERLAP.csv")
    with open(out1, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # ---- one row per TestRail case
    crows = []
    for s in sorted(by_test):
        cl = verdict.get(s)
        if not cl:
            continue
        for cid in sorted(by_test[s]):
            c = cases[cid]
            crows.append(
                {
                    "testrail_case": "C%d" % cid,
                    "case_id": cid,
                    "title": clean(c["title"]),
                    "suite_id": c["suite_id"],
                    "priority": PRIORITY.get(
                        c.get("priority_id"), c.get("priority_id")
                    ),
                    "automation_coverage": COVERAGE.get(
                        c.get("custom_automation_coverage")
                    ),
                    "starfox_test": s,
                    "verdict": cl["tier"],
                    "in_tree_tests": clean(cl["tests"]),
                }
            )
    crows.sort(key=lambda r: (r["verdict"], r["starfox_test"], r["case_id"]))
    out2 = os.path.join(OUT, "STARFOX_TREE_OVERLAP_cases.csv")
    with open(out2, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(crows[0].keys()))
        w.writeheader()
        w.writerows(crows)

    # ---- summary
    tier_tests = collections.Counter(r["verdict"] for r in rows)
    tier_cases = collections.Counter(r["verdict"] for r in crows)
    per_suite = collections.defaultdict(collections.Counter)
    for r in rows:
        per_suite[r["starfox_suite"]][r["verdict"]] += 1

    lines = [
        "| STARfox suite | Tests | STRONG (duplicated) | % | PARTIAL | UNIQUE |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for d in sorted(per_suite, key=lambda d: -per_suite[d]["STRONG"]):
        c = per_suite[d]
        tot = sum(c.values())
        lines.append(
            "| %s | %d | **%d** | %d%% | %d | %d |"
            % (
                d,
                tot,
                c["STRONG"],
                round(100 * c["STRONG"] / tot),
                c["PARTIAL"],
                c["UNIQUE"],
            )
        )
    tot = len(rows)
    lines.append(
        "| **Total** | **%d** | **%d** | **%d%%** | **%d** | **%d** |"
        % (
            tot,
            tier_tests["STRONG"],
            round(100 * tier_tests["STRONG"] / tot),
            tier_tests["PARTIAL"],
            tier_tests["UNIQUE"],
        )
    )
    with open(os.path.join(HERE, "summary.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    # ---- housekeeping
    linked = set(by_test)
    untested = sorted(pop.repo_tests() - linked)
    hk = ["# Round-5 housekeeping findings", ""]
    hk.append(
        "## TestRail points at STARfox tests that no longer exist (%d)" % len(dead)
    )
    hk.append("")
    hk.append(
        "`custom_automated_test_names` names a file that is not in the repo. Either the "
        "test was renamed and TestRail was not updated, or it was deleted while the case "
        "stayed marked as automated."
    )
    hk.append("")
    hk.append("| Cited path | Cases |")
    hk.append("|---|---|")
    for name in sorted(dead):
        hk.append("| `%s` | %s |" % (name, ", ".join("C%d" % i for i in dead[name])))
    hk.append("")
    hk.append(
        "## Cases marked as STARfox-covered with no usable test name (%d)"
        % len(unlinked)
    )
    hk.append("")
    hk.append("| Case | Title |")
    hk.append("|---|---|")
    for cid in unlinked:
        hk.append("| C%d | %s |" % (cid, clean(cases[cid]["title"])[:100]))
    hk.append("")
    hk.append("## STARfox tests no TestRail case points at (%d)" % len(untested))
    hk.append("")
    hk.append(
        "Not necessarily a problem -- some are meta/harness tests -- but any real feature "
        "test here is running in CI without a TestRail case recording that fact."
    )
    hk.append("")
    for p in untested:
        hk.append("- `%s`" % p)
    with open(os.path.join(HERE, "housekeeping.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(hk) + "\n")

    print("STARfox-automated cases (coverage 2 or 3): %d" % len(pop.population()))
    print("linked to distinct STARfox tests:          %d" % len(by_test))
    print(
        "  with a verdict: %d   remaining: %d"
        % (len(verdict.keys() & by_test.keys()), len(missing))
    )
    print()
    print(
        "By STARfox test:  STRONG %d   PARTIAL %d   UNIQUE %d"
        % (tier_tests["STRONG"], tier_tests["PARTIAL"], tier_tests["UNIQUE"])
    )
    print(
        "By TestRail case: STRONG %d   PARTIAL %d   UNIQUE %d"
        % (tier_cases["STRONG"], tier_cases["PARTIAL"], tier_cases["UNIQUE"])
    )
    print()
    print(
        "housekeeping: %d dead links, %d unlinked cases, %d untested STARfox files"
        % (len(dead), len(unlinked), len(untested))
    )
    if dupes:
        print(
            "!! %d STARfox tests claimed by more than one cluster: %s"
            % (len(dupes), list(dupes)[:8])
        )
    print()
    print("wrote", os.path.relpath(out1, OUT))
    print("wrote", os.path.relpath(out2, OUT))
    print()
    print("\n".join(lines))


main()
