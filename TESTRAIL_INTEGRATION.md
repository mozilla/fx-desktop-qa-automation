# TestRail Integration

STARfox uses [TestRail](https://www.testrail.com/) as the system of record for smoke / functional / L10N test results on Firefox Beta, DevEdition, and RC builds. This document explains how the integration is wired up: the modules that talk to the API, the pytest hooks that drive the reporting, and the CI workflows that decide when a run should be reported.

## Files at a glance

| File | Role |
|---|---|
| [`modules/testrail.py`](modules/testrail.py) | Thin HTTP wrapper. `APIClient` handles auth, GET/POST, and error logging. `TestRail` exposes the endpoints the rest of the codebase uses (`get_test_case`, `create_new_plan`, `create_new_plan_entry`, `create_test_run_on_plan_entry`, `update_test_cases`, etc.). |
| [`modules/testrail_integration.py`](modules/testrail_integration.py) | The integration brain. Builds plan titles, decides whether a session is *reportable*, walks the pytest JSON report, and creates/updates plans/entries/runs/results in TestRail. |
| [`conftest.py`](conftest.py) | pytest hooks: `pytest_configure` early-exits if the session isn't reportable; `pytest_sessionfinish` posts results when the run is over. |
| [`scripts/check_reportable.sh`](scripts/check_reportable.sh) | The job-level gate used by the scheduled workflows — runs `reportable()` (or `preview_reportable()` for dry-runs) and writes `win`/`mac` outputs the downstream jobs key off. |
| [`modules/taskcluster.py`](modules/taskcluster.py) | Provides `get_tc_secret()` — pulls TestRail credentials from Taskcluster secrets when the Linux runs execute on TC. |

## TestRail vocabulary (as used here)

- **Project** — `TESTRAIL_FX_DESK_PRJ = 17`, "Firefox Desktop".
- **Milestone** — `Firefox <major>` (e.g. `Firefox 151`).
- **Submilestone** — channel-scoped child of the major milestone: `Beta 151`, `Devedition 151`, etc. (`Rc`/`Devedition` fall back to the `Beta` submilestone if their own doesn't exist.)
- **Plan** — one per Firefox build, named e.g. `[Beta 151] Automated testing 151.0b9-build1`. L10N runs prefix with `L10N `. Functional splits append ` - Functional (Split N)`.
- **Entry** — one per test suite inside a plan. The entry's `name` is the suite description; its `suite_id` matches a TestRail suite.
- **Run** — one per (entry, config) pair. The `config` string ("Configuration") encodes platform / OS / arch, e.g. `MacOS 15 arm64`. For L10N, the region is prepended: `de-Windows 11 x86_64`.
- **Configuration group** — `CONFIG_GROUP_ID = 95`. New configs (e.g. a new platform string) are auto-created in this group via `add_config`.
- **Case** — a single TestRail test case, identified by id. STARfox tests provide their case id via a `test_case` pytest fixture.

## End-to-end flow

```mermaid
flowchart TD
    A[GitHub Actions trigger<br/>schedule / PR / manual] --> B[Check-*-Version job<br/>scripts/check_reportable.sh]
    B -->|reportable | preview_reportable| C{reportable?}
    C -- no --> Z[Job emits win=False/mac=False<br/>downstream jobs skip]
    C -- yes --> D[main.yml / main-l10n.yml<br/>Test-Windows / Test-MacOS / L10N-Linux]
    D -->|sets TESTRAIL_REPORT=true| E[pytest run]
    E --> F[conftest.pytest_configure<br/>calls tri.reportable, exits if False]
    E --> G[Tests execute, JSON report accumulates]
    G --> H[conftest.pytest_sessionfinish<br/>calls tri.collect_changes + tri.mark_results]
    H --> I[(TestRail<br/>plan / entry / run / results)]
    H --> J[.tmp_testrail_info<br/>plan_title and config record]
```

The integration is *defensive about double-reporting*: both `reportable()` (pre-flight, at the job-gating level) and `collect_changes()` (post-run, at the result-posting level) check the existing plan structure and skip work that already exists.

## Pre-flight: `reportable()` and `preview_reportable()`

Both live in `modules/testrail_integration.py` and share `_common_reportable_context()`, which gathers local info **without touching TestRail**:

- platform (passed in or detected from `_platform.system()`),
- Firefox version via `scripts/collect_executables.py -n`,
- channel (`FX_CHANNEL` env var, defaulting to `beta`, title-cased),
- plan title via `get_plan_title()`,
- the expected suite IDs for the current `STARFOX_SPLIT`,
- L10N expectations via `scripts/choose_l10n_ci_set.py:select_l10n_mappings()` when `FX_L10N` is set.

### `reportable(platform_to_test=None) -> bool`

Used by the workflow gates and `conftest.pytest_configure`. Returns `True` when the run should proceed to TestRail. The decision tree:

1. `TESTRAIL_REPORT` env var must be truthy — otherwise return `False`.
2. `REPORTABLE=true` short-circuits to `True` (used by the headed re-runs to force a second pass).
3. `TESTRAIL_BASE_URL` / `TESTRAIL_USERNAME` / `TESTRAIL_API_KEY` must be present.
4. Open a session via `testrail_init()`; bail on failure.
5. The major milestone (`Firefox N`) and channel submilestone must exist.
6. If the split is empty (and not L10N), return `False`.
7. Look up the plan in the submilestone:
   - if it doesn't exist yet → `True` (we'll create it).
   - otherwise, compare the runs already on the plan against expectations:
     - **L10N**: count `(site, region, platform)` mappings already covered; report only if `covered < expected`.
     - **STARfox**: compute `expected_suites − covered_suites` for this platform; report only if uncovered suites remain.

### `preview_reportable(platform_to_test=None) -> dict`

The dry-run variant. Same context, but returns a JSON-shaped dict and explicitly does **not** query TestRail. Used by `check_reportable.sh` when `DRY_RUN=true` to print what *would* happen.

### `get_plan_title(version_str, channel)`

Parses the Firefox version string and assembles the plan name using `TESTRAIL_RUN_FMT`:

```
[{channel} {major}] {plan_prefix}Automated testing {major}.{minor}b{beta}-build{build}
```

Three regexes cover the channel variants:

| Channel | Version pattern | Example title |
|---|---|---|
| Beta | `FX_PRERC_VERSION_RE` (`151.0b9-build1`) | `[Beta 151] Automated testing 151.0b9-build1` |
| Devedition | `FX_DEVED_VERSION_RE` (`151.0b9`) | `[Devedition 151] Automated testing 151.0b9` |
| Rc | `FX_RC_VERSION_RE` (`151.0-build3`) | `[Rc 151] Automated testing 151.0-build3` |

When `FX_L10N` is set, `L10N ` is prefixed inside the brackets. When `STARFOX_SPLIT` starts with `functional`, ` - Functional (Split N)` is appended.

## Post-run: `collect_changes()` → `organize_entries()` → `mark_results()`

Fires from `conftest.pytest_sessionfinish` once pytest has produced its `_json_report.report`. End-to-end:

1. **`collect_changes(tr_session, report)`** (`testrail_integration.py:893`)
   - Reads the first test's `metadata` (set by the test) for `fx_version` and `machine_config`.
   - On Linux, post-processes `machine_config` with `lsb_release` to get `Linux 24.04 x86_64`.
   - For L10N, prepends `FX_REGION` → `de-Linux 24.04 x86_64`.
   - Recomputes the plan title, finds (or creates) the milestone, submilestone, and plan.
   - Writes `.tmp_testrail_info` (plan title `|` config) so other tools can pick up the reporting target.
   - Adds/updates an "execution link" line in the plan's description so each plan has a clickable link back to the Action / TC log per OS (`replace_link_in_description`).
   - Finds (or creates) the config in `CONFIG_GROUP_ID = 95`.
   - Buckets tests by `suite_id`, then for each suite hands off to `organize_entries`.
2. **`organize_entries(tr_session, expected_plan, suite_info)`** (`testrail_integration.py:719`)
   - Re-fetches the plan to avoid stale-snapshot races between the Mac and Windows jobs.
   - Ensures the entry for this suite exists (creates it if not, with `config_ids` and `runs` — see the [related fix](#known-pitfalls)).
   - Ensures the run for this `(entry, config)` pair exists; creates it via `create_test_run_on_plan_entry` if not.
   - If existing run is missing any of the expected case ids, calls `update_run_in_entry` to add them.
   - Skips runs marked `is_completed`.
   - Returns results grouped into `passed` / `failed` / `xfailed` / `skipped` buckets, keyed by `run_id`.
3. **`mark_results(tr_session, test_results)`** (`testrail_integration.py:542`)
   - For each non-skipped category, fetches the current statuses on the run.
   - Won't downgrade an already-passing case to anything else.
   - Posts the batch via `update_test_cases` → `add_results_for_cases/{run_id}`.

## How a session decides to report

Reporting is opt-in per-process, gated by environment variables:

| Variable | Purpose |
|---|---|
| `TESTRAIL_REPORT` | Master switch. Must be truthy for any TestRail call to be made. |
| `REPORTABLE` | Force-report override. Used by the **headed re-run** steps in `main.yml` / `main-l10n.yml` so that the second pass always reports even when `reportable()` would otherwise return `False`. |
| `TESTRAIL_BASE_URL` / `TESTRAIL_USERNAME` / `TESTRAIL_API_KEY` | Credentials. Sourced from GitHub Secrets in CI, or from Taskcluster secrets when running on Linux via TC (`get_tc_secret()`). |
| `FX_CHANNEL` | `beta` (default), `devedition`, or `rc`. Drives plan title / submilestone lookup. |
| `FX_L10N` | When set, switches to L10N mode (entry-per-site, run-per-region/platform). |
| `FX_REGION` / `CM_SITE` | L10N region and site identifiers. Encoded into the config string and the entry name. |
| `STARFOX_SPLIT` | The split being run (`smoke`, `functional1`, `functional2`, ...). Affects plan title and which suites count toward "covered". |
| `MANUAL` | Set by the manual-dispatch path. Limits run to smoke set. |

## Workflow trigger points

| Workflow | Trigger | Channel | Reports? | Notes |
|---|---|---|---|---|
| [`smoke-test-beta.yml`](.github/workflows/smoke-test-beta.yml) | `schedule: 30 */1 * * *`, `workflow_dispatch` | Beta | Yes | Runs `Check-Beta-Version` job → `check_reportable.sh` → calls reusable `main.yml`. `STARFOX_SPLIT=smoke`. |
| [`functional-test-beta.yml`](.github/workflows/functional-test-beta.yml) | `schedule: 12 * * * *`, `workflow_dispatch` | Beta | Yes | Picks a functional split deterministically from the current hour (`functional$(date +%-I % MAX_SPLITS + 1)`), then runs the standard check + main flow. |
| [`smoke-test-devedition.yml`](.github/workflows/smoke-test-devedition.yml) | `schedule: 35 */1 * * *`, `workflow_dispatch` | DevEdition | Yes | Same shape as smoke-beta but with `FX_CHANNEL=devedition`. |
| [`smoke-test-rc.yml`](.github/workflows/smoke-test-rc.yml) | `schedule: 55 */4 * * *`, `workflow_dispatch` | RC | Yes | `FX_CHANNEL=rc`. Falls back to the `Beta N` submilestone if `Rc N` doesn't exist. |
| [`test-l10n-beta.yml`](.github/workflows/test-l10n-beta.yml) | `schedule: 40 */2 * * *` | Beta (L10N) | Yes | `FX_L10N=true`. Calls `reportable()` once per platform (Windows/Darwin/Linux) and dispatches `main-l10n.yml`. |
| [`main.yml`](.github/workflows/main.yml) | `workflow_call`, `workflow_dispatch` | inherited | Conditional | The actual test executor. Sets `TESTRAIL_REPORT=true` only in the *Scheduled Beta* path (`is_pull_request==false` and not dry-run). The headed re-run step exports `REPORTABLE=true` so it always reports. PR / dry-run / manual-installer paths leave `TESTRAIL_REPORT=false`. |
| [`main-l10n.yml`](.github/workflows/main-l10n.yml) | `workflow_call`, `workflow_dispatch` | inherited | Conditional | Same pattern as `main.yml` but with `FX_L10N=true` and per-region matrix. |
| [`ci-dispatch.yml`](.github/workflows/ci-dispatch.yml) | `pull_request`, `workflow_dispatch` | Beta | **No** | PR / manual triggers pass `is_pull_request: true` to `main.yml`, which keeps `TESTRAIL_REPORT=false`. PR runs intentionally never write to TestRail. |
| [`main-stability.yml`](.github/workflows/main-stability.yml) / [`stability-test-dispatch.yml`](.github/workflows/stability-test-dispatch.yml) | `workflow_dispatch` (stability monitoring) | Beta | **No** | Stability runs hardcode `TESTRAIL_REPORT=false` / `REPORTABLE=false`. See [`STABILITY_MONITORING.md`](./STABILITY_MONITORING.md). |

## The dry-run / preview path

When the dispatch workflows are kicked off with `dry_run=true`:

1. `check_reportable.sh` calls `preview_reportable("Windows")` and `preview_reportable("Darwin")` instead of `reportable()`.
2. The outputs are marked `win=Preview` / `mac=Preview` so the gating `needs.Check-*.outputs.win_reportable == 'True'` condition stays false → downstream test jobs are skipped.
3. `preview_json` (a JSON blob with the would-be plan title, expected suites, etc.) is captured and printed by the `Preview-Plan` job via `scripts/test_beta_preview_plan.sh`.

Dry-run never opens a TestRail session and never modifies any state.

## Execution link in plan description

`replace_link_in_description()` is called by `collect_changes()` to embed a per-OS execution link in each TestRail plan's description, so a reviewer in TestRail can click through to:

- a TaskCluster log (for Linux runs that set `TASKCLUSTER_PROXY_URL`), or
- a GitHub Actions run (Windows / Mac via `GITHUB_REPOSITORY` + `GITHUB_RUN_ID`).

If a line for the same OS already exists, it's replaced rather than duplicated.

## Known pitfalls

- **`add_plan_entry` rejects entries with `config_ids` but no `runs`.** TestRail returns `Field :entries has configurations but no test runs.` if you pass `config_ids` without also passing a matching `runs` array. `create_new_plan_entry` in `modules/testrail.py` builds a one-run-per-config payload automatically when the caller doesn't supply `runs`. See the [TestRail Plans API](https://support.testrail.com/hc/en-us/articles/7077711537684-Plans).
- **Mac and Windows jobs can race.** Both platforms start with the same plan snapshot from `collect_changes`. Without the re-fetch at the top of `organize_entries`, both can decide "this entry doesn't exist yet" and create duplicate, configless entries. The re-fetch is what keeps this safe.
- **Rerun outcomes lose pass/fail info.** When a pytest test reports `outcome: rerun`, `collect_changes` falls back to `test["call"]["outcome"]` to recover the underlying status.
- **Already-passing cases are never downgraded.** `mark_results` queries the run's existing results and filters out any case currently marked `passed (status_id=1)` before posting an update. So flaky reruns can't turn a green case red.

## Helper scripts

Adjacent one-shots that use the same `testrail_init()` session — useful for maintenance:

- [`modules/testrail_scripts/set_empty_automation_status_to_untriaged.py`](modules/testrail_scripts/set_empty_automation_status_to_untriaged.py)
- [`modules/testrail_scripts/set_coverage_none_for_untriaged_suitable_unsuitable_disabled_automation.py`](modules/testrail_scripts/set_coverage_none_for_untriaged_suitable_unsuitable_disabled_automation.py)
- [`modules/testrail_scripts/testrail_script_set_all_subs_to_functional.py`](modules/testrail_scripts/testrail_script_set_all_subs_to_functional.py)
- [`modules/testrail_scripts/testrail_status_analyses.py`](modules/testrail_scripts/testrail_status_analyses.py)
- [`scripts/validate_cases.py`](scripts/validate_cases.py) — sanity check that test files reference existing TestRail case IDs.

These run locally (or from a developer's machine) against the same env-var configuration as the CI path.