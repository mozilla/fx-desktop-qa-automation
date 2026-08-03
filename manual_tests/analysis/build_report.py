"""Generate the low-priority candidate list from the per-suite verdict files.

Outputs:
  manual_tests/LOW_PRIORITY_CANDIDATES.csv   - one row per STRONG case, for TestRail import
  manual_tests/analysis/summary.md           - the tables pasted into
                                               FIREFOX_TEST_COVERAGE_COMPARISON.md Part 5
"""

import csv
import glob
import importlib
import os
import sys
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import _ledger  # noqa: E402

for f in sorted(glob.glob(os.path.join(HERE, "d_*.py"))):
    importlib.import_module(os.path.basename(f)[:-3])

CASES = _ledger.cases()
BY_ID = {}
for c in CASES:
    BY_ID.setdefault(c["id"], c)  # 9 ids are duplicated rows in the export

SUITE_NAMES = {
    65334: "Address Bar 138+",
    2241: "Preferences",
    43517: "Password manager",
    5833: "Security and Privacy",
    29219: "Downloads",
    2054: "Form Autofill",
    2525: "Bookmarks Toolbar (+ History/Library)",
    65: "Find in page / PDF viewer",
    42945: "about:firefoxview",
    70279: "AI window / Smart Window",
    23035: "Easy Setup onboarding",
    2103: "Tabbed Browser",
    53810: "Sidebar",
    100482: "Share Folder / Curated Link Sharing",
    59371: "Terms of Service onboarding",
    103289: "Onboarding (Smart Window, 2nd suite)",
    68: "Session Restore",
    2119: "Profiles",
    943: "Screenshots",
    2085: "Find Toolbar",
    100943: "Saved credentials autofill dropdown",
    69070: "Local Network / Device Access",
    70723: "Rename tabs (Tab Notes)",
    100547: "Private Window appearance (NOVA)",
    73783: "Reduced Protection (PBM/ETP)",
    76427: "ToU onboarding on Linux distros",
    2126: "Reader View",
    498: "Geolocation",
    71394: "Translate quick action / about:translations",
}

# TestRail custom_automation_status == 4 means "already automated in STARfox".
STARFOX = {c["id"] for c in CASES if c.get("custom_automation_status") == 4}


def rows(tier):
    out = []
    for cl in _ledger.CLUSTERS:
        if cl["tier"] != tier:
            continue
        for cid in cl["ids"]:
            c = BY_ID.get(cid)
            if not c:
                continue
            out.append(
                {
                    "case_id": cid,
                    "title": c["title"].strip(),
                    "suite_id": cl["suite"],
                    "suite_name": SUITE_NAMES.get(cl["suite"], str(cl["suite"])),
                    "section_id": c["section_id"],
                    "priority_id": c["priority_id"],
                    "already_automated_in_starfox": "yes" if cid in STARFOX else "",
                    "in_tree_tests": cl["tests"],
                    "why": cl["why"],
                }
            )
    out.sort(key=lambda r: (r["suite_name"], r["section_id"], r["case_id"]))
    return out


def main():
    strong = rows("STRONG")
    out_csv = os.path.join(HERE, "..", "LOW_PRIORITY_CANDIDATES.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(strong[0].keys()))
        w.writeheader()
        w.writerows(strong)

    per_suite = collections.Counter(r["suite_id"] for r in strong)
    total_per_suite = collections.Counter(c["suite_id"] for c in CASES)
    med = collections.Counter(
        cl["suite"] for cl in _ledger.CLUSTERS if cl["tier"] == "MEDIUM" for _ in cl["ids"]
    )

    lines = []
    lines.append("| Suite | TestRail suite | Cases | STRONG (de-prioritise) | % | Reviewed-but-kept |")
    lines.append("|---|---|---:|---:|---:|---:|")
    reviewed = sorted({cl["suite"] for cl in _ledger.CLUSTERS},
                      key=lambda s: -per_suite.get(s, 0))
    for sid in reviewed:
        n = per_suite.get(sid, 0)
        tot = total_per_suite[sid]
        lines.append(
            "| %d | %s | %d | **%d** | %d%% | %d |"
            % (sid, SUITE_NAMES.get(sid, sid), tot, n, round(100 * n / tot), med[sid])
        )
    lines.append(
        "| | **Total (%d suites reviewed)** | **%d** | **%d** | **%d%%** | **%d** |"
        % (
            len(reviewed),
            sum(total_per_suite[s] for s in reviewed),
            len(strong),
            round(100 * len(strong) / sum(total_per_suite[s] for s in reviewed)),
            sum(med.values()),
        )
    )

    with open(os.path.join(HERE, "summary.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    print("wrote", out_csv, len(strong), "rows")
    print("already automated in STARfox too:",
          sum(1 for r in strong if r["already_automated_in_starfox"]))
    print("\n".join(lines))


main()
