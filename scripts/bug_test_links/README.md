# Bug-test links and Test Yield

Finds the desktop Firefox bugs filed since a start date, works out which tests found
them, and scores each test's **Test Yield**. Results go to BigQuery dataset `fx_qa_ci`.

```
Bugzilla ───┐
Treeherder ─┼─► bug_test_links_to_bq.py ─► bugzilla_bugs, bug_test_links,
TestRail ───┤                                testrail_executions
tests/ ─────┘                                         │
                                                      ▼
fx_qa_ci.test_results ───────────────► test_yield_to_bq.py ─► test_yield
```

1. **Collect** ([`bug_test_links_to_bq.py`](../bug_test_links_to_bq.py) and this
   folder) reads the sources and writes bugs, bug–test links and TestRail executions.
2. **Score** ([`test_yield_to_bq.py`](../test_yield_to_bq.py)) reads only BigQuery, so
   it can be re-run with other weights without collecting again.

## Running it

**`bug-test-links-to-bq.yml`** collects, then calls the score workflow. It's scheduled
for Wednesdays at 08:00 UTC, but `release_check.py` lets it run only every second
Wednesday from 2026-11-25, and only after a major Firefox release in the past 14 days.
Runs never overlap; a new one waits.

| Input | Default | Meaning |
|---|---|---|
| `since_date` | `2026-10-13` | Only bugs and TestRail runs created on or after it |
| `load_mode` | `incremental` | `incremental` fetches what changed since the last load; `full` rebuilds every table |
| `score_yield` | on | Score after loading |

**`test-yield-to-bq.yml`** scores only. Run it by hand to try other weights.

| Input | Default | Meaning |
|---|---|---|
| `since_date` | `2026-10-13` | Use the same date as the load |
| `weights` | from `yield_config.toml` | e.g. `U=0.3,F=0.2,S=0.3,R=0.2`; positive, summing to 1 |

The secrets are `GC_CREDENTIAL_STABILITY`, `BQ_PROJECT` and, for collect only,
`TESTRAIL_BASE_URL`, `TESTRAIL_USERNAME` and `TESTRAIL_API_KEY`. Bugzilla and
Treeherder are read anonymously, so only public bugs are seen.

Locally, set the same variables plus `BQ_DATASET` and `SINCE_DATE`, then run
`uv run python -m scripts.bug_test_links_to_bq` or `-m scripts.test_yield_to_bq`.

## Which bugs count

A bug is in scope if it's public, created since `since_date`, not in product
`Mozilla QA`, on a desktop OS, and one of:

- platform **Desktop**;
- platform **All** in product **Firefox**;
- platform **Unspecified** with the `intermittent-failure` keyword, and at least one
  desktop failure on Treeherder.

Treeherder failures count only on desktop platforms (`linux*`, `windows*`, `macosx*`)
and on trees that carry landed Firefox code: `autoland`, `mozilla-central`,
`mozilla-beta`, `mozilla-release` and `mozilla-esr*`. Try is left out, since a failure
there may come from the patch under test.

Only bugs that link to a test are stored.

## How a bug is linked to a test

Each link has a `source` (`starfox`, `in_tree` or `testrail`), a `test_key` and a
`test_key_type` (`path`, `label` or `testrail_case`).

**From the bug summary**, in order:

1. A test file path. It's a `starfox` link if a STARfox test's path ends with it,
   otherwise `in_tree`.
2. A STARfox test file or function name without a path.
3. For an intermittent bug with neither, the text before the first `|`, after
   Treeherder's prefixes ("Intermittent", "Perma", "TEST-UNEXPECTED-…") are stripped.
   It's an `in_tree` `label`, or a `path` if it looks like one.

| Summary | Link |
|---|---|
| `Intermittent browser/…/browser_label_and_icon.js \| single tracking bug` | `in_tree`, the path |
| `Intermittent leakcheck \| default 1552 bytes leaked` | `in_tree`, `leakcheck` (`label`) |
| `test_open_new_tab fails because the tab strip moved` | `starfox`, `tests/tabs/test_open_new_tab.py` |
| `Intermittent dom/tests/test_open_new_tab.js \| timed out` | `in_tree`, since it isn't the STARfox file |

**From TestRail:** a result with status Failed or Failed (new) links each bug ID in its
Defects field, one link per bug per result, keyed `C<case id>`. A case's refs field
isn't used: it means the case covers a bug, not that it found it.

## Loading

Both modes write rows to `staging_*` tables, then apply them in one BigQuery
transaction (`tables.merge_sql()`). If the merge fails, nothing changes. Running the
same merge twice leaves the tables unchanged.

- **Incremental** fetches bugs created or changed since the last load, newer TestRail
  results, and any unchanged bug a new result points at. Re-fetched bugs get fresh
  summary links; a bug now out of scope loses its row and all its links.
- **Full** empties the tables first. It runs by itself only when there's no earlier
  load. If `since_date` differs from the last load's, an incremental run stops; use
  `load_mode=full` to change the period.
- **Treeherder keeps about 120 days.** An incremental load never lowers a stored
  failure count, so aged-out failures can't drop a bug. A full load can't fetch them
  again.

## Scoring

```
Test Yield = 100 × (wU·U + wF·F + wS·S + wR·R)
```

| | Component | From |
|---|---|---|
| U | Unique bugs found | Bugs linked to the test, log-scaled |
| F | Failure-detection rate | Detections ÷ executions |
| S | Severity | Summed bug impact, from severity only; priority isn't used in triage |
| R | Regressions caught | Release cycles with a regression found ÷ cycles run |

Only defects count, not INVALID, WORKSFORME, INCOMPLETE or DUPLICATE ones.
Intermittent bugs don't count either: they mostly point at a flaky test rather than a
product defect. They stay in `bugzilla_bugs`, flagged `is_intermittent`. Each
component is scaled 0–1 across all tests. A component a test has no data for is left
out, and the other weights are scaled up. In-tree tests, for example, have no
executions, so no F.

A TestRail case that a STARfox test automates is scored as that test. Its executions
come from STARfox CI (`fx_qa_ci.test_results`), or from TestRail if CI has none.

The defaults are in [`yield_config.toml`](yield_config.toml): the weights and the
severity scale. The `weights` workflow input overrides the weights for one run.

## Tables (`fx_qa_ci`)

| Table | One row per | Notes |
|---|---|---|
| `bugzilla_bugs` | In-scope bug with a link | Bugzilla fields, `firefox_status` per version, `is_intermittent`, `desktop_failure_count` / `_platforms` |
| `bug_test_links` | Bug–test link | Link fields above; TestRail links add plan, run, config, Firefox version and result |
| `testrail_executions` | Valid TestRail result | Any status but Untested, Blocked, Retest or Skipped |
| `bug_test_links_state` | Last load (one row) | `since_date`, `loaded_at` (the next cutoff), `mode` |
| `desktop_bugs_with_tests` | Link, joined to its bug | View, recreated on every load |
| `test_yield` | Scored test | Raw counts, U/F/S/R, `yield_score`, ranks, weights used; replaced on every run |
