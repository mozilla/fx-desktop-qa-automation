# Manual-suite ↔ Firefox-tree coverage analysis

Produces **`manual_tests/LOW_PRIORITY_CANDIDATES.csv`** — the list of manual TestRail cases whose
user flow is already covered by automated tests inside
[mozilla-firefox/firefox](https://github.com/mozilla-firefox/firefox), so the manual team can
de-prioritise them during crunch time.

The narrative write-up is **Part 5 of `FIREFOX_TEST_COVERAGE_COMPARISON.md`** in the repo root.

## Layout

| File | Role |
|---|---|
| `_ledger.py` | Shared collector. `C(...)` records a verdict for a list of case ids; `CSEC(...)` does the same for whole TestRail sections (used where a section is a repetition matrix). |
| `d_01_*.py` … `d_13_*.py` | **The analysis, as data.** 312 clusters. Each holds: tier (`STRONG` / `MEDIUM`), the in-tree test paths, the rationale, and the case ids it applies to. Edit these to change a verdict. |
| `build_report.py` | Loads the ledger, joins case titles/sections from the export, writes the CSV and `summary.md`. |
| `validate_paths.py` | Checks every tree path cited in the ledger against a cached tree inventory. Catches typos and stale filenames. |
| `summary.md` | Generated per-suite results table (pasted into Part 5 §5.2). |

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

### 2. `.fxtree/` — the Firefox tree inventory (only needed by `validate_paths.py`)

~53 MB, not committed. Rebuild with the GitHub git-trees API: fetch the recursive tree for each
top-level subtree of interest (`browser`, `toolkit`, `devtools`, `services`, `accessible`, `dom`,
`netwerk`, `security`, `uriloader`, `intl`, `widget`, `extensions`, `docshell`, `image`, `modules`),
then write:

- `.fxtree/allfiles.json` — flat list of every file path
- `.fxtree/bc.json` — just the browser-chrome tests (`basename` starts with `browser_`, ends `.js`,
  path contains `/test`)

`q.py` in that folder is a small regex search helper over those two files.

## Usage

```bash
python manual_tests/analysis/build_report.py     # regenerate the CSV + summary.md
python manual_tests/analysis/validate_paths.py   # re-check every cited tree path
```

## Refreshing after the tree moves

The analysis is a point-in-time snapshot (`main` @ `7d438b9`, 2026-07-30). Before a release cycle:
rebuild `.fxtree/`, run `validate_paths.py`, fix anything that no longer resolves, then re-run
`build_report.py`.
