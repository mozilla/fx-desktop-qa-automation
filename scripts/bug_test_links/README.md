# Bug-test links and Test Yield

These scripts find the desktop Firefox bugs filed since a start date, work out which
tests found them, and score each test's **Test Yield**. Everything lands in BigQuery,
dataset `fx_qa_ci`.

```
Bugzilla ───┐
Treeherder ─┼─► bug_test_links_to_bq.py ─► bugzilla_bugs, bug_test_links,
TestRail ───┤      (this package)            testrail_executions  (BigQuery)
tests/ ─────┘                                         │
                                                      ▼
fx_qa_ci.test_results ───────────────► test_yield_to_bq.py ─► test_yield
```

There are two stages:

1. **Collect.** [`scripts/bug_test_links_to_bq.py`](../bug_test_links_to_bq.py) and the
   modules in this folder read Bugzilla, Treeherder, TestRail and the STARfox `tests/`
   folder, and write the bugs, their links to tests and TestRail executions.
2. **Score.** [`scripts/test_yield_to_bq.py`](../test_yield_to_bq.py) reads only
   BigQuery and writes one Test Yield row per test. It doesn't call Bugzilla, TestRail
   or Treeherder, so it can be re-run with other weights without collecting again.

## GitHub Actions

### Add Bug to Test Links to BigQuery (`.github/workflows/bug-test-links-to-bq.yml`)

Collects the data, then scores it.

**Triggers:**

- **Schedule:** every Wednesday at 08:00 UTC. The `check` job lets the run continue
  only every second Wednesday from 2026-11-25, and only if a major Firefox release
  shipped in the past 14 days.
- **Manual run**, with these inputs:

| Input | Default | Meaning |
|---|---|---|
| `since_date` | `2026-10-13` | Start of the analysis period: only bugs created on or after it, and TestRail runs created on or after it |
| `load_mode` | `incremental` | `incremental` fetches only what changed since the last load; `full` rebuilds every table |
| `score_yield` | on | Run the scoring workflow after the load |

Scheduled runs use the defaults. Runs never overlap: a new one waits for the one in
progress (`concurrency` group `bug-test-links-to-bq`).

A full load rebuilds from the sources. Treeherder failures older than about 120 days
can't be fetched again, so after a full load, older intermittent bugs can have lower
counts, or be gone.

**Jobs, in order:**

1. **`check`.** Checks out only `scripts/bug_test_links/release_check.py` and runs it
   with plain `python3`, with no install. It outputs `run` (`true` or `false`) and the
   `since_date` to use. Manual runs always get `run=true`.
2. **`ingest`.** Runs only if `check` said `run=true`. It installs dependencies with
   `uv sync`, signs in to Google Cloud and runs
   `uv run python -m scripts.bug_test_links_to_bq`.
3. **`score`.** Runs only if `ingest` succeeded, and on scheduled runs or when
   `score_yield` is on. It calls the workflow below with the same `since_date`, and
   passes the secrets on (`secrets: inherit`).

**Secrets:**

- `GC_CREDENTIAL_STABILITY`: the Google Cloud service account;
- `BQ_PROJECT`;
- `TESTRAIL_BASE_URL`, `TESTRAIL_USERNAME` and `TESTRAIL_API_KEY`.

Bugzilla and Treeherder are read anonymously.

### Score Test Yield in BigQuery (`.github/workflows/test-yield-to-bq.yml`)

Scores the data already in BigQuery. It is called by the workflow above, and can also
be run by hand, for example to try other weights.

| Input | Default | Meaning |
|---|---|---|
| `since_date` | `2026-10-13` (required when called) | Start of the analysis period; use the same date as the load |
| `weights` | empty: the values in `yield_config.toml` | Component weights for this run, e.g. `U=0.3,F=0.2,S=0.3,R=0.2`; positive and summing to 1 |
| `severity_weight` | empty: the value in `yield_config.toml` | Severity's share of a bug's impact for this run, 0–1; priority gets the rest |

To change the defaults, edit [`yield_config.toml`](yield_config.toml). It holds the
component weights, severity's share, and the severity and priority scales. The inputs
above override the first two for a single run. The scales can only be changed in the
file.

It has one job, which installs dependencies, signs in to Google Cloud and runs
`uv run python -m scripts.test_yield_to_bq`. It needs only `GC_CREDENTIAL_STABILITY` and
`BQ_PROJECT`, not TestRail.

## Files

### `scripts/bug_test_links_to_bq.py`: the collect entry point

**`collect(cutoff, stored)`** gathers everything one load writes. With no `cutoff`, it
gathers everything since `SINCE_DATE`. With a `cutoff`, the time of the last load, it
gathers only what changed after it. In order, it:

1. Reads TestRail through `testrail_links()`: failed results that list a bug, and
   every valid execution. With a cutoff, only newer results.
2. Searches Bugzilla through `search_bugs()`. With a cutoff, only bugs created **or
   changed** after it.
3. With a cutoff, fetches by ID (`fetch_bugs()`) any bug that a new TestRail result
   points at but that was neither fetched in step 2 nor loaded before. A new result
   can name a bug that hasn't changed.
4. Keeps the bugs that pass `in_scope()`, then runs `add_treeherder_failures()`. That
   adds desktop failure counts to intermittent bugs, and drops platform-Unspecified
   bugs with none.
5. Builds the summary links (`summary_links()`) for every bug kept.
6. Adds the TestRail links whose bug is either kept in step 4, or loaded before and
   not fetched again. A bug that wasn't fetched again keeps its earlier scope decision.
7. Keeps only the bugs that link to a test, counting TestRail links already loaded.

It returns:

- `bugs`;
- `links`;
- `executions`;
- `checked`: the IDs of every bug fetched in this run. The merge uses them to
  refresh or remove those bugs' old rows.

**`main()`** runs one load:

1. Checks `LOAD_MODE`, and records the start time, which becomes the next cutoff.
2. Reads the saved state with `last_load()`. If there's none, it switches to a full
   load and logs why. If its `since_date` differs from this run's, an incremental run
   stops with an error, so a mistyped date can't rebuild every table. To change the
   period, run with `load_mode` `full`.
3. **Full load:** deletes the state row first, so a run that fails part way is
   followed by another full one, then calls `collect()`.
   **Incremental load:** reads the IDs and failure counts of the bugs already loaded,
   and the IDs of those with a TestRail link, then calls `collect(cutoff, stored)`.
4. Turns the result into rows. Bugs go through `bug_row()`. Links and executions get
   an `ingested_at` time.
5. **Full load only:** recreates the four main tables empty.
6. Writes each set of rows to a `staging_*` table, runs the merge transaction from
   `merge_sql()`, then deletes the staging tables. Both modes write this way. In a full
   load, merging into empty tables inserts everything.
7. Recreates the view `desktop_bugs_with_tests`.

### `common.py`: shared settings and helpers

| Name | What it does |
|---|---|
| `SINCE_DATE` | Start of the analysis period, from the `SINCE_DATE` variable (default `2026-10-13`). Also used by the score stage. |
| `HEADERS` | A User-Agent that identifies these requests to Bugzilla and Treeherder |
| `since_epoch()` | `SINCE_DATE` as a Unix timestamp, the format TestRail's filters use |
| `epoch_to_iso()` | A TestRail Unix timestamp as an ISO date and time |
| `get_json(url, params)` | A GET request. On a rate limit (HTTP 429) it waits for `Retry-After` seconds and tries again, five attempts in all; any other error is raised. |

### `bugzilla.py`: Bugzilla and Treeherder

**Settings:**

| Name | Contents |
|---|---|
| `SCOPE_QUERIES` | The three Bugzilla searches: platform Desktop; product Firefox with platform All; platform Unspecified with the `intermittent-failure` keyword |
| `EXCLUDED_PRODUCTS` | `Mozilla QA`, whose bugs ask for a STARfox test to be fixed |
| `DESKTOP_OS` | macOS, Linux, Unspecified, All. Anything starting with "Windows" also counts. |
| `DESKTOP_TREEHERDER_PLATFORMS` | Treeherder platform prefixes that count as desktop: `linux`, `windows`, `macosx` |
| `FIREFOX_TREES` | The Treeherder trees whose failures count: `autoland`, `mozilla-central`, `mozilla-beta`, `mozilla-release`, plus any `mozilla-esr*`. These carry only landed Firefox code. **Try** and project branches are left out, because a failure there may come from the unreviewed patch being tested. Thunderbird's `comm-*` trees are left out too. |
| `BUG_FIELDS` | The fields requested for each bug, including `cf_status_firefox140` to `199` (Bugzilla ignores the ones that don't exist yet) |

**Functions:**

| Function | What it does |
|---|---|
| `search_bugs(changed_since)` | Runs each scope query for bugs created since `SINCE_DATE`, 500 a page, ordered by ID. With `changed_since`, it adds Bugzilla's `last_change_time` filter. It returns every match, **in scope or not**, so the merge can also see bugs that dropped out. |
| `fetch_bugs(ids)` | Fetches the given bugs, 200 per request. Without `BUGZILLA_API_KEY` (the workflow sets none), Bugzilla returns only public bugs. |
| `in_scope(bug)` | All the scope rules in one place: public, created since `SINCE_DATE`, not Mozilla QA, on a desktop OS, and platform Desktop, or All in product Firefox, or Unspecified and intermittent. Applied to every fetched bug, because bugs fetched by ID didn't come through a scope query. |
| `is_intermittent(bug)` | The `intermittent-failure` keyword, or a summary starting with "Intermittent" or "Perma" |
| `is_firefox_tree(tree)` | True for a tree in `FIREFOX_TREES` or starting with `mozilla-esr` |
| `desktop_failures(bug_id)` | Asks Treeherder's `failuresbybug` API for the bug's failures since `SINCE_DATE`, and counts them per platform. Only failures on a desktop platform **and** a Firefox tree count. |
| `add_treeherder_failures(bugs, earlier)` | Calls `desktop_failures()` for every intermittent bug and stores the counts, then drops platform-Unspecified bugs with no desktop failure. Treeherder keeps only about 120 days of failures. So when a loaded bug's stored count (`earlier`) is higher than today's, it keeps the stored count and adds the stored platforms. That stops old failures ageing out from lowering a count, or from dropping a bug along with its TestRail links. |

### `summary.py`: test names in bug summaries

**Patterns:**

| Name | Matches |
|---|---|
| `TEST_PATH_RE` | A test file path, with `/` or `\` separators and an optional leading `/` (WPT), ending in a test extension (`.js`, `.html`, `.py`, `.toml` and others); or a bare `browser_*` / `test_*` file name |
| `SUMMARY_PREFIX_RE` | The prefixes Treeherder puts before the test in a summary, so they can be stripped: "Intermittent", "Perma", "Frequent", "TV", "TVW", "TEST-UNEXPECTED-…", "[tier 2]" and similar |
| `CASE_ID_RE` | The TestRail case ID in a STARfox test's `test_case` fixture |

**Functions:**

| Function | What it does |
|---|---|
| `starfox_tests()` | Reads every `tests/**/test_*.py` file. It maps each file name, and each top-level `test_…` function in it, to the file's path and TestRail case ID. |
| `starfox_name_re(tests)` | One pattern matching any of those names as a whole word, longest first. `test_search` doesn't match inside `test_search.js`. |
| `summary_links(bug, tests, name_re)` | The tests a bug's summary names, as links. See [How a bug is linked to a test](#how-a-bug-is-linked-to-a-test). |

### `testrail.py`: TestRail results and executions

**Settings:**

| Name | Contents |
|---|---|
| `FAILED_STATUSES` | Failed and Failed (new): the only statuses whose Defects field links a bug |
| `NOT_EXECUTED_STATUSES` | Untested, Blocked, Retest and Skipped. Any other status is a valid execution. |
| `BUG_ID_RE` | A 6–8 digit bug ID that isn't part of a Jira key such as `DTE-123456` |
| `FX_VERSION_RE` | A Firefox version in a run name, e.g. `150.0b3-build1` |

**`TestRailReader`** wraps the repo's TestRail client (`modules/testrail.py`), using
the three TestRail secrets:

| Method | What it does |
|---|---|
| `get(uri)` | One API call. On a rate limit it waits a minute and tries again, five attempts in all. |
| `paged(uri, key)` | Yields every item of a list endpoint, 250 a page |
| `milestones()` | Every milestone in project 17, with its parent's name, e.g. *Beta 159* → *Firefox 159* |
| `statuses()` | Status ID → name |

**Functions:**

| Function | What it does |
|---|---|
| `milestone_context(milestones, id)` | A plan's release (*Firefox 159*) and channel milestone (*Beta 159*) |
| `finished_before(item, cutoff)` | True if a plan or run was completed before the cutoff, and so can't have newer results |
| `runs_since(reader, milestones, cutoff)` | Yields every run created since `SINCE_DATE`: the runs in each plan, then standalone runs. Each comes with its plan name, channel (from `[Beta 159]` at the start of the plan name), release and entry name. With a cutoff, it skips plans and runs completed before it. |
| `testrail_links(reader, cutoff)` | For each run, reads its results (only those created after the cutoff, if given), and its tests, to find each result's case. It returns two lists: **executions**, one row per valid result; and **links**, one per bug ID in the Defects field of a Failed or Failed (new) result. |

### `tables.py`: BigQuery tables

| Name | What it does |
|---|---|
| Table name constants | `BUGS_TABLE`, `LINKS_TABLE`, `EXECUTIONS_TABLE`, `STATE_TABLE`, `CHECKED_TABLE` (staging only), `STAGING_PREFIX` and `VIEW` |
| `bug_row(bug, ingested_at)` | A Bugzilla bug as a `bugzilla_bugs` row. It adds the Firefox status flags per version, the intermittent flag, the desktop failure count and platforms, and the bug's URL. |
| `schemas()` | Each table's columns and clustering, keyed by table name |
| `replace_table(client, table_id, rows, schema, clustering)` | Deletes and recreates a table, then loads the rows. It works with no rows. |
| `merge_sql(dataset, bug_columns)` | The SQL transaction that applies the staging tables to the loaded ones (below) |
| `last_load(client, table_id)` | The saved state row, or None if there isn't one |

**The merge transaction** runs these steps in one BigQuery transaction. If it fails,
the loaded tables keep their contents from before the merge. In a full load, they
were already emptied and the state row deleted, so the next run is full again.

1. For every bug fetched in this run (`staging_checked_bugs`), deletes its summary
   links. If the bug is no longer kept (out of scope, or no link left), it also deletes
   its TestRail links and its row.
2. Updates or inserts the bugs from `staging_bugzilla_bugs`.
3. Inserts the new summary links.
4. Inserts the TestRail links not already present, matched on result and bug.
5. Inserts the executions not already present, matched on result.
6. Replaces the state row, with this run's `since_date`, start time and mode.

Applying the same staging tables twice leaves the loaded tables unchanged.

### `release_check.py`: the schedule decision

It runs on its own in the workflow's `check` job, and uses only Python's standard
library, so that job needs no install. The score stage imports its
`major_releases()`; the collect modules don't use it.

| Name | What it does |
|---|---|
| `FIRST_RUN`, `RUN_EVERY_DAYS`, `RELEASE_WINDOW_DAYS` | 2026-11-25, 14 and 14 |
| `is_run_day(today)` | True on `FIRST_RUN` and every 14 days after. GitHub's cron can't say "every two weeks", so the workflow wakes weekly and this skips alternate Wednesdays. |
| `released_recently(today, release_dates)` | True if a major release shipped in the 14 days before today |
| `major_releases()` | Every major release (date and version) from Mozilla's product-details service: one entry per major version, so dot releases such as 159.0.1 don't count as a release. The score stage reuses it for release cycles. |
| `should_run(event, today)` | Manual runs always go ahead. Scheduled runs need a run day and a recent release. |
| `main()` | Writes `run=true` or `run=false` to `$GITHUB_OUTPUT` |

### `scripts/test_yield_to_bq.py`: the score entry point

| Name | What it does |
|---|---|
| `load_config()` | Reads `yield_config.toml` into `CONFIG`, when the module loads. `YIELD_WEIGHTS` and `YIELD_SEVERITY_WEIGHT`, if set, replace the file's weights and severity share. The weights must be positive and sum to 1, and every share and scale value must be 0–1. Otherwise it exits with the name of the bad value. |
| `release_dates()` | Every major release from `major_releases()`, plus the next one from product-details |
| `cycle_of(day, releases)` | The release cycle a date falls in, named after the version that ships at its end |
| `bug_impact(bug)` | A bug's severity and priority combined on a 0–1 scale |
| `automated_cases()` | TestRail case ID → path of the STARfox test that automates it, read from the STARfox files |
| `merge_automated_executions(executions, automated)` | Counts an automated case's executions once, under its STARfox test. STARfox CI reports its runs to TestRail, so TestRail's copy is used only if CI has none. |
| `normalized(values, scale)` | Divides each value by the largest one, after an optional scale such as `math.log1p` |
| `yield_score(parts, weights)` | 100 × the weighted sum of a test's components. A missing component is left out, and the other weights are scaled up to sum to 1. |
| `score(links, bugs, executions, cycles, weights, automated)` | Groups the links into tests, computes each test's components and Test Yield, and ranks them overall and within each source |
| `main()` | Reads the bugs, links and executions from BigQuery (STARfox executions from `fx_qa_ci.test_results`), runs `score()`, and replaces `test_yield` |

## How a bug is linked to a test

Every link in `bug_test_links` records three things:

- `source`: where the link came from;
- `test_key`: which test;
- `test_key_type`: how exact that key is.

### From bug summaries (`summary.summary_links()`)

Each bug kept by `collect()` has its summary checked in three passes:

1. **Test file paths** (`TEST_PATH_RE`). Backslashes are turned into `/`. If a STARfox
   test's path ends with the path found, it's a **`starfox`** link to that test, with
   the test's TestRail case ID. So `tests/tabs/test_open_new_tab.py`,
   `tabs/test_open_new_tab.py` and `test_open_new_tab.py` all match. Otherwise it's an
   **`in_tree`** link, keyed by the path.
2. **STARfox names without a path** (`starfox_name_re`). A STARfox file name or test
   function on its own, e.g. "test_open_new_tab fails …", is a `starfox` link. If the
   same test was already found in pass 1, it's not added twice.
3. **Intermittents naming no test file.** If passes 1 and 2 found nothing and the bug
   is intermittent, the Treeherder prefixes are stripped (`SUMMARY_PREFIX_RE`), and the
   text before the first `|` becomes an `in_tree` link with type **`label`**. If that
   text looks like a path (it contains `/` and no spaces), it counts as a `path`
   instead. That happens with a tracking bug for a group of tests.

Each test appears at most once per bug.

| Summary | Link |
|---|---|
| `Intermittent browser/components/sessionstore/test/browser_label_and_icon.js \| single tracking bug` | `in_tree`, `browser/components/sessionstore/test/browser_label_and_icon.js`, `path` |
| `Intermittent /css/CSS2/backgrounds/background-root-010.xht \| Testing …` | `in_tree`, `/css/CSS2/backgrounds/background-root-010.xht`, `path` |
| `Perma [tier2] browser/…/creditCard/browser_creditCard_capture \| single tracking bug` | `in_tree`, the path prefix, `path` (pass 3) |
| `Intermittent leakcheck \| default 1552 bytes leaked` | `in_tree`, `leakcheck`, `label` |
| `tests\smart_window\test_c4438277_group_related_tabs.py hangs` | `starfox`, `tests/smart_window/test_c4438277_group_related_tabs.py`, case 4438277 |
| `test_open_new_tab fails because the tab strip moved` | `starfox`, `tests/tabs/test_open_new_tab.py`, case 134453 |
| `Intermittent dom/tests/test_open_new_tab.js \| timed out` | `in_tree`, `dom/tests/test_open_new_tab.js`, because it isn't the STARfox file |

### From TestRail (`testrail.testrail_links()`)

A result links a bug when **both** of these hold:

- its status is **Failed** or **Failed (new)**;
- its **Defects** field contains the bug ID (`BUG_ID_RE`).

Other statuses, such as Passed or Blocked, don't link a bug, even with a bug in
Defects.

- **One link per bug per result.** A result listing two bugs gives two links. A case
  that failed on three configurations with the same bug gives three links, one per
  result.
- **Keyed by case.** The `test_key` is `C<case id>` and the type is `testrail_case`.
  The link carries the run's context: release, channel milestone, channel, plan,
  entry, run, configuration and Firefox version. It also carries the result's status
  and date.
- **Kept only for kept bugs.** A TestRail link is stored only if its bug is in scope
  (see `collect()` step 6).
- **Case refs aren't used.** A case's refs field means "this case covers the bug", not
  "this case found it".

## Tables

All tables are in `fx_qa_ci`. The collect stage writes the first four and the view;
the score stage writes `test_yield`.

### `bugzilla_bugs`: one row per in-scope bug that links to a test

| Columns | Contents |
|---|---|
| `bug_id`, `url` | The bug and its Bugzilla link |
| `summary`, `product`, `component`, `platform`, `op_sys` | As in Bugzilla |
| `status`, `resolution`, `type`, `severity`, `priority` | As in Bugzilla |
| `keywords`, `regressed_by` | Repeated fields |
| `firefox_status` | One entry per Firefox version with a status flag set, e.g. `{version: "159", status: "affected"}` |
| `is_intermittent` | From `bugzilla.is_intermittent()` |
| `desktop_failure_count`, `desktop_failure_platforms` | Treeherder failures on desktop since `SINCE_DATE`; intermittent bugs only |
| `creation_time`, `last_change_time` | As in Bugzilla |
| `ingested_at` | When this load wrote the row |

Clustered by `product` and `component`. Merged by `bug_id`.

### `bug_test_links`: one row per bug–test link

| Columns | Contents |
|---|---|
| `bug_id` | The bug |
| `source`, `test_key`, `test_key_type`, `case_id` | Which test, as described in [How a bug is linked to a test](#how-a-bug-is-linked-to-a-test) |
| `case_title`, `suite_id` | TestRail case title and suite (TestRail links only) |
| `release`, `channel_milestone`, `channel` | E.g. *Firefox 159*, *Beta 159*, *Beta* (TestRail links only) |
| `plan_id`, `plan_name`, `entry_name` | The TestRail plan and entry (TestRail links only) |
| `run_id`, `run_name`, `run_config`, `fx_version` | The TestRail run, its configuration (OS) and Firefox version (TestRail links only) |
| `testrail_test_id`, `result_id`, `result_status`, `result_created_at` | The TestRail result (TestRail links only) |
| `ingested_at` | When this load wrote the row |

Clustered by `source` and `test_key`. Summary links are replaced each time their bug is
fetched again. TestRail links are matched on `result_id` and `bug_id`.

### `testrail_executions`: one row per valid TestRail execution

| Columns | Contents |
|---|---|
| `result_id` | The TestRail result |
| `case_id` | Its case |
| `executed_on` | The result's date |
| `ingested_at` | When this load wrote the row |

Clustered by `case_id`. Matched on `result_id`, so a result is never counted twice. The
score stage counts these rows per case and day.

### `bug_test_links_state`: one row

| Columns | Contents |
|---|---|
| `since_date` | The period start of the last load |
| `loaded_at` | When the last load started; the next incremental load fetches what changed after it |
| `mode` | `full` or `incremental` |

### `desktop_bugs_with_tests` (view)

Each link joined to its bug: every `bugzilla_bugs` column except `ingested_at`, then
every `bug_test_links` column except `bug_id` and `ingested_at`. Only bugs with a link
appear. It's recreated on every load.

### `staging_*` tables

`staging_bugzilla_bugs`, `staging_bug_test_links`, `staging_testrail_executions` and
`staging_checked_bugs` exist only during a load. They hold the rows the merge is about
to apply, and are deleted after it.

### `test_yield`: one row per scored test

Written by `test_yield_to_bq.py`; every run replaces it.

| Columns | Contents |
|---|---|
| `source`, `test_key`, `case_id` | The test. An automated TestRail case appears under its STARfox test. |
| `bugs_found`, `detections`, `executions`, `impact`, `regression_cycles`, `executed_cycles` | The raw counts behind the components |
| `u_score`, `f_score`, `s_score`, `r_score` | The components, from 0 to 1. Empty if the test has no data for one. |
| `yield_score` | Test Yield, from 0 to 100 |
| `missing_components` | Components the test has no data for, e.g. `F` for in-tree tests |
| `rank`, `rank_in_source` | Position overall, and within the test's source |
| `weights`, `window_start`, `cycles`, `computed_at` | The weights, period and release cycles used, and when the row was written |

Clustered by `source` and `rank`.
