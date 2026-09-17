"""Build the Critical / not-yet-automated overlap report.

Population: priority_id == 4 (Critical) AND custom_automation_status != 4 (Automation status
is anything other than Completed).

Outputs:
  manual_tests/CRITICAL_NOT_AUTOMATED_STRONG.csv  - one row per STRONG-overlap case
  manual_tests/analysis/crit_summary.md           - per-suite table

A case is STRONG when an in-tree test in mozilla-firefox/firefox drives the same user flow
and asserts the same user-visible outcome. MEDIUM means the tree touches the feature but at
narrower scope or lower altitude, so the manual case stays in rotation.
"""

import collections
import csv
import glob
import importlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import _ledger  # noqa: E402
import crit_pop  # noqa: E402

for f in sorted(glob.glob(os.path.join(HERE, "c_*.py"))):
    importlib.import_module(os.path.basename(f)[:-3])

POP = crit_pop.population()
NAMES = crit_pop.SUITE_NAMES
STATUS = crit_pop.AUTOMATION_STATUS


def clean(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def main():
    verdict = {}
    for cl in _ledger.CLUSTERS:
        for cid in cl["ids"]:
            if cid in POP:
                verdict[cid] = cl

    # ---- integrity checks
    stray = [cid for cl in _ledger.CLUSTERS for cid in cl["ids"] if cid not in POP]
    dupes = collections.Counter(
        cid for cl in _ledger.CLUSTERS for cid in cl["ids"] if cid in POP
    )
    dupes = {k: v for k, v in dupes.items() if v > 1}
    missing = sorted(set(POP) - set(verdict))

    rows = []
    for cid, cl in verdict.items():
        if cl["tier"] != "STRONG":
            continue
        c = POP[cid]
        rows.append(
            {
                # TestRail refers to cases as C<id>; that is the form the manual team uses.
                "testrail_case": "C%d" % cid,
                "case_id": cid,
                "title": clean(c["title"]),
                "suite_id": c["suite_id"],
                "suite_name": NAMES.get(c["suite_id"], str(c["suite_id"])),
                "section_id": c["section_id"],
                "automation_status": STATUS.get(
                    c.get("custom_automation_status"), c.get("custom_automation_status")
                ),
                "in_tree_tests": clean(cl["tests"]),
                "why": clean(cl["why"]),
            }
        )
    rows.sort(key=lambda r: (r["suite_name"], r["section_id"], r["case_id"]))

    # Per-suite listing of the C-numbers, for pasting into TestRail filters / the write-up.
    by_suite = collections.defaultdict(list)
    for r in rows:
        by_suite[r["suite_name"]].append(r["testrail_case"])
    with open(
        os.path.join(HERE, "crit_strong_case_numbers.md"), "w", encoding="utf-8"
    ) as fh:
        fh.write(
            "# Critical, not-yet-automated cases with a STRONG in-tree overlap\n\n"
        )
        fh.write("TestRail case numbers, grouped by suite.\n")
        for name in sorted(by_suite):
            fh.write("\n## %s  (%d)\n\n" % (name, len(by_suite[name])))
            fh.write(", ".join(by_suite[name]) + "\n")

    out = os.path.join(HERE, "..", "CRITICAL_NOT_AUTOMATED_STRONG.csv")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # ---- summary table
    strong = collections.Counter(r["suite_id"] for r in rows)
    med = collections.Counter(
        POP[cid]["suite_id"] for cid, cl in verdict.items() if cl["tier"] == "MEDIUM"
    )
    total = collections.Counter(c["suite_id"] for c in POP.values())
    reviewed = sorted(
        {POP[cid]["suite_id"] for cid in verdict}, key=lambda s: -strong.get(s, 0)
    )

    lines = [
        "| Suite | TestRail suite | Critical & not automated | STRONG overlap | % | Reviewed-but-kept |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for sid in reviewed:
        n, tot = strong.get(sid, 0), total[sid]
        lines.append(
            "| %d | %s | %d | **%d** | %d%% | %d |"
            % (sid, NAMES.get(sid, sid), tot, n, round(100 * n / tot), med.get(sid, 0))
        )
    tot_reviewed = sum(total[s] for s in reviewed)
    lines.append(
        "| | **Total (%d suites)** | **%d** | **%d** | **%d%%** | **%d** |"
        % (
            len(reviewed),
            tot_reviewed,
            len(rows),
            round(100 * len(rows) / tot_reviewed),
            sum(med.values()),
        )
    )
    with open(os.path.join(HERE, "crit_summary.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    print("population (Critical, not Automation Completed): %d" % len(POP))
    print("with a verdict: %d   remaining: %d" % (len(verdict), len(missing)))
    print("STRONG overlap: %d" % len(rows))
    print("reviewed but kept: %d" % sum(med.values()))
    if stray:
        print("!! %d cluster ids outside the population: %s" % (len(stray), stray[:10]))
    if dupes:
        print(
            "!! %d cases claimed by more than one cluster: %s"
            % (len(dupes), list(dupes)[:10])
        )
    print("wrote", os.path.normpath(out))
    print()
    print("\n".join(lines))


main()
