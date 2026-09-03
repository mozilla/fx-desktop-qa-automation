# Glean Telemetry Tests

Tests that verify Firefox records the expected Glean SERP telemetry after a search action.
They live in `tests/glean/` and follow a dataset-driven pattern rather than the usual
one-test-file-per-case convention.

## How it works

The tests read telemetry straight from the Glean JS API in the chrome context, instead of
going through the `about:glean` UI. A test does three things:

1. run a user flow (for example a URL bar search)
2. poll the metric with `testGetValue()`
3. assert the recorded payload

Polling replaces fixed sleeps: Glean records asynchronously, so the test retries until the
metric appears or the timeout is reached. Each case runs in a fresh profile, so only events
from that scenario are present.

## Structure

```
tests/glean/
├── conftest.py          # suite_id, prefs_list, add_to_prefs_list
├── flows.py             # entry / action / abandonment flow registry
├── utils.py             # load_cases, skip_if_unstable
│
├── misc_metrics/        # cases.json + test_misc_metrics.py
├── sap_counts/
├── serp_abandonment/
├── serp_engagement/
└── serp_impression/
```

One folder per metric family. Each holds a `cases.json` dataset and a single test file with
the automation logic. Logic stays in Python, data stays in JSON — adding an engine, region or
partner code means editing JSON only.

`modules/browser_object_glean.py` holds the `Glean` BOM. It runs JS in the chrome context, so
it is a BOM.

## Dataset format

Each entry in `cases.json`:

```json
{
  "id": "3255425",
  "entry": "urlbar",
  "action": null,
  "params": {"engine": "Google"},
  "prefs": [["browser.search.region", "US"]],
  "expected": {"provider": "google", "partner_code": "firefox-b-1-d",
               "source": "urlbar", "tagged": "true"}
}
```

| Field | Meaning |
|---|---|
| `id` | TestRail case ID, returned by the `test_case` fixture |
| `entry` | registered entry flow name from `flows.py` |
| `action` | optional post-SERP action flow name, or `null` |
| `params` | flow inputs, most often `engine` |
| `prefs` | Firefox prefs set before launch, on top of `ENTRY_PREFS` |
| `expected` | payload subset that must match the recorded event |
| `expected_keys` | optional; fields checked for presence only, when the value changes every run |
| `unstable` | optional; see below |

Every folder except `misc_metrics` tests a single metric, declared once at the top of
`cases.json`. `misc_metrics` holds cases for five different metrics, so there `metric` is a
field on each case instead.

## Flows

`flows.py` is the shared registry. A flow is a function registered under a name that matches
the value used in `cases.json`:

- `@_entry` — how the SERP is opened (`urlbar`, `searchbar`, `urlbar_handoff`, `contextmenu`,
  `urlbar_searchmode`, `urlbar_persisted`, …)
- `@_action` — what happens after the SERP loads (`reload`, `open_in_new_tab`, `tabhistory`,
  `click_non_ads_link`)
- `@_abandonment` — how the user leaves the SERP (`tab_close`, `window_close`, `navigation`,
  `back_navigation`, `refresh_navigation`)

Tests call `run_entry`, `run_action` and `run_abandonment`, which look the name up and raise
`NotImplementedError` if it is missing. Fixing a flow fixes every case that uses it.

## Unstable flag

`key.yaml` can only mark a whole test file, and a Glean test file covers dozens of cases. To
take one case out of the run without disabling the rest, add an `unstable` reason to that case
in `cases.json`:

```json
{
  "id": "3255427",
  "entry": "urlbar_handoff",
  "action": null,
  "params": {"engine": "Google"},
  "prefs": [["browser.search.region", "US"]],
  "expected": {"provider": "google", "partner_code": "firefox-b-1-d",
               "source": "urlbar_handoff", "tagged": "true"},
  "unstable": "bug 1234567 - handoff records source='urlbar' instead of 'urlbar_handoff'"
}
```

`skip_if_unstable` is called from the `case` fixture, so the skip happens before `driver`
starts — the browser never launches and the case reports as Untested. Remove the key to bring
the case back.

Only use it for Firefox-side flaws: a regression, a metric that stopped recording, a flow the
browser no longer supports. Always name the bug.

Do not use it for external reasons. A search engine serving a bot challenge is not a Firefox
defect, and skipping it up front hides a case that would pass on a rerun.
`block_if_bot_challenge` covers that at runtime instead: called from the test's `except` block,
it turns a Cloudflare "just a moment" page into a Blocked skip and lets every other failure
propagate.

## Running

```bash
pytest tests/glean                          # whole suite
pytest tests/glean/serp_impression          # one metric family
pytest tests/glean -k 3255425               # one case, by TestRail ID
pytest tests/glean -k urlbar_handoff        # one entry: urlbar/searchbar/contextmenu/...
pytest tests/glean -k tab_close             # one action: reload/open_in_new_tab/...
pytest tests/glean -k 3255425 -s --log-cli-level=INFO   # debug one case with live logs
```

`-k` matches the test ID, built from the dataset — `3255425-urlbar`, `3255492-urlbar-reload`,
`3255574-Bing-searchbar`, `3255543`. So entry and action work, engine only in `sap_counts`, and
the metric name never does (`-k serp.adImpression` selects nothing) — use the folder or the ID.

A failing poll prints expected vs actual against the closest recorded event, so the timeout
message usually shows which field is off.

## CI

Glean runs as its own `glean` test set, separate from the regular functional splits.

When the `glean` test set is selected, CI runs the `tests/glean` folder directly rather than
selecting individual files through the normal split logic.

Glean runs on Windows, macOS and Linux for pull requests, Beta and RC. Windows and macOS come
from GitHub Actions, all through `main.yml`: `ci-dispatch.yml` for pull requests,
`glean-test-beta.yml` and `glean-test-rc.yml` for Beta and RC. Linux comes from Taskcluster:
`run-glean-tests` for pull requests, `new-beta-glean` and `new-rc-glean` for Beta and RC. The
shared `core.yml` workflow supports all three platforms itself and is reached from
`nightly.yml`, which is dispatch-only — it has no schedule, so nightly Glean runs are not
automatic.

`manifests/key.yaml` registers the Glean test files under the `glean` split. Since each test
file is parametrized over many cases, file-level manifest status cannot represent the health
of an individual case; the `unstable` field in `cases.json` is used for that.

## TestRail

Suite `S70197`, "Glean Telemetry". Because the tests are parametrized, `test_case` returns the
`id` of the current case instead of a hardcoded value, and the reporting chain picks it up as
usual.

A `pytest.skip` inside the Glean suite is mapped to `blocked` in `organize_entries`
(`modules/testrail_integration.py`), so only skip on a confirmed external condition that a
rerun could clear.

## Known limits

- **Google** serves an "unusual traffic" captcha to CI IPs. Counters recorded at search-issue
  time still work, but any flow needing a post-search step on the page must use Bing or DDG.
- **Ads metrics** (`withads`, `adclicks`, `serp.adImpression`) only work on Bing: Google is
  captcha'd and DDG serves no ads.
- **Ecosia** gets a Cloudflare challenge from CI datacenter IPs. Progress tracked over time,
  there are signs it self-heals on a recurring interval. A workaround may still be worth
  finding, to avoid parking the cases back to manual.
- **Execution time**: one Firefox instance per case. Deliberate — sharing a profile risks false
  positives from residual telemetry.
