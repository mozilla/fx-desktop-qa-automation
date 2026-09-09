# Manual-suite ↔ Firefox-tree coverage analysis

Which manual TestRail cases have their user flow already covered by automated tests inside
[mozilla-firefox/firefox](https://github.com/mozilla-firefox/firefox)?

Two outputs, from two passes over the corpus:

| Output | Population | Write-up |
|---|---|---|
| `manual_tests/LOW_PRIORITY_CANDIDATES.csv` | All priorities, 29 suites (rounds 1–3) | Part 5 of `FIREFOX_TEST_COVERAGE_COMPARISON.md` |
| `manual_tests/CRITICAL_NOT_AUTOMATED_STRONG.csv` | **Priority = Critical** and **Automation status ≠ Completed**, all 57 suites that contain such cases (round 4) | Part 6 |

Round 4 is the more actionable of the two: those cases are the ones most likely to be both
scheduled for manual execution *and* queued for STARfox automation, so a duplicate costs twice.
Cases there are named the way TestRail names them — `C` + the export's `id`, e.g. `C3163606`.

## Layout

Shared:

| File | Role |
|---|---|
| `_ledger.py` | Shared collector. `C(...)` records a verdict for a list of case ids; `CSEC(...)` does the same for whole TestRail sections (used where a section is a repetition matrix). |
| `fetch_tree.py` | Rebuilds `.fxtree/` from the GitHub git-trees API. Run this first if the snapshot is stale. |

Rounds 1–3 (all priorities):

| File | Role |
|---|---|
| `d_01_*.py` … `d_13_*.py` | **The analysis, as data.** 312 clusters. Each holds: tier (`STRONG` / `MEDIUM`), the in-tree test paths, the rationale, and the case ids it applies to. Edit these to change a verdict. |
| `build_report.py` | Loads the ledger, joins case titles/sections from the export, writes the CSV and `summary.md`. |
| `validate_paths.py` | Checks every tree path cited in the `d_*` ledger against the cached tree inventory. |
| `summary.md` | Generated per-suite results table (pasted into Part 5 §5.2). |

Round 4 (Critical, not-yet-automated):

| File | Role |
|---|---|
| `crit_pop.py` | Defines the population (`priority_id == 4` and `custom_automation_status != 4`) and the suite-name map. |
| `crit_sheet.py` | Worksheet dumper. `python crit_sheet.py` for the overview, `crit_sheet.py <suite>` for one suite by section, `--steps` to inline the manual steps, `--todo` for suites still missing verdicts. |
| `c_util.py` | `CT()` clusters by case *title* and `CREST()` clusters a suite's remainder — both for the repetition-matrix suites, where listing ids by hand invites transcription errors. |
| `c_01_*.py` … `c_11_*.py` | **The round-4 analysis, as data.** Same cluster shape as `d_*.py`. |
| `c_10_prior_rounds.py` | Replays the rounds 1–3 verdicts for the 482 population cases they already assessed, instead of re-deriving them. A later `c_*` verdict wins over a carried-over one. |
| `build_crit_report.py` | Writes `CRITICAL_NOT_AUTOMATED_STRONG.csv`, `crit_summary.md` and `crit_strong_case_numbers.md`. Fails loudly on double-claimed cases or ids outside the population. |
| `validate_crit_paths.py` | Checks every tree path cited in the `c_*` ledger. Also accepts mid-path abbreviations by unique-suffix match. |

**Tiers:** `STRONG` = an in-tree test drives the same UI flow and asserts the same user-visible
outcome → goes in the CSV. `MEDIUM` = the tree touches the feature but at narrower scope or lower
altitude (pref-only, telemetry-only, one variant of a matrix) → stays in the manual rotation.

## Required inputs (both gitignored)

### 1. `manual_tests/all_cases.json` — the TestRail export

~30 MB, not committed. Re-export the full case corpus from TestRail as JSON, one object per case
with at least `id`, `title`, `suite_id`, `section_id`, `priority_id` and
`custom_automation_status`. E.g. via the TestRail API:

```
GET /index.php?/api/v2/get_cases/{project_id}&suite_id={suite_id}
```

concatenated across suites into a single top-level JSON array.

### 2. `.fxtree/` — the Firefox tree inventory (needed by the `validate_*_paths.py` scripts)

~65 MB, not committed. Rebuild it with:

```bash
python manual_tests/analysis/fetch_tree.py
```

That fetches the recursive tree for each top-level subtree of interest and writes:

- `.fxtree/<subtree>.json` — paths under that subtree
- `.fxtree/allfiles.json` — flat list of every file path
- `.fxtree/bc.json` — just the browser-chrome tests (`basename` starts with `browser_`, ends `.js`,
  path contains `/test`)
- `.fxtree/HEAD` — the commit the snapshot was taken at

Set `GITHUB_TOKEN` if you hit the unauthenticated rate limit. `testing/` exceeds the API's tree
limit and comes back truncated; that only affects web-platform-tests, which this analysis does not
cite. `q.py` in that folder is a small regex search helper over `allfiles.json` and `bc.json`:

```bash
python .fxtree/q.py "backup/tests/browser_"        # browser-chrome tests only
python .fxtree/q.py --all "components/backup/"     # every file
```

## Usage

```bash
python manual_tests/analysis/fetch_tree.py            # refresh the tree inventory first

# rounds 1-3 (all priorities)
python manual_tests/analysis/build_report.py          # LOW_PRIORITY_CANDIDATES.csv + summary.md
python manual_tests/analysis/validate_paths.py

# round 4 (Critical, not-yet-automated)
python manual_tests/analysis/crit_sheet.py --todo     # what still lacks a verdict
python manual_tests/analysis/build_crit_report.py     # CRITICAL_NOT_AUTOMATED_STRONG.csv + tables
python manual_tests/analysis/validate_crit_paths.py
```

## Refreshing after the tree moves

Both analyses are point-in-time snapshots — rounds 1–3 against `main` @ `7d438b9` (2026-07-30),
round 4 against `5069177` (2026-08-12). Before a release cycle: re-run `fetch_tree.py`, then the
two `validate_*_paths.py` scripts, fix anything that no longer resolves, then re-run the two
`build_*` scripts.

Coverage in the tree only grows over time, so a stale snapshot understates the overlap rather than
overstating it — a `STRONG` verdict does not go bad for lack of a test. What does go stale is the
*cited path*, when a test is renamed or moved; that is what the validators catch.
