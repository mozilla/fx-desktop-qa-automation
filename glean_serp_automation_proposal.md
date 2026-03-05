# Glean SERP Telemetry Automation Proposal

## Overview

This document proposes a scalable automation strategy for the Firefox Desktop SERP Glean telemetry test suite.

Glean is Mozilla's structured telemetry system — the library Firefox uses to collect product metrics (events, counters, timings, etc.) and send them in telemetry pings.

---

## Infrastructure

### Approach Exploration

Before implementing automation for Glean SERP telemetry, several approaches were evaluated to determine the most reliable way to validate that a search action records the expected telemetry event.

**1. DevTools Console**
Run `Glean.serp.impression.testGetValue()` from the browser DevTools console.
- Useful for manual debugging
- Not automatable with Selenium — DevTools cannot be reliably controlled

**2. Direct Glean JS API execution**
Execute `Glean.serp.impression.testGetValue()` through Selenium using `execute_script`.
- Retrieves telemetry values directly from the Glean API
- Avoids UI interaction entirely
- Allows polling until telemetry data becomes available

**3. about:glean UI verification**
Automate the about:glean Metrics Table and inspect the JSON payload for the metric.
- Closest to manual verification
- Requires many UI interactions and relies on experimental page elements, making automation fragile

### Selected Approach

The preferred solution is **Option 2: Direct Glean JS API execution**. This approach provides the best balance between reliability, speed, and automation stability. Instead of navigating the about:glean UI, the test retrieves telemetry data directly from the Glean API using Selenium.

The test:
1. Performs the user action (e.g. a URL bar search)
2. Polls the Glean metric using `testGetValue()`
3. Validates the payload recorded by Firefox

This avoids fragile UI selectors and ensures that tests focus on the telemetry system itself rather than the debugging interface. Polling the metric allows the test to wait for telemetry data without relying on fixed delays.

---

## Proposal Restructuring

A working proof of concept already exists (`test_glean_serp_impression_js_api.py`), and the core telemetry polling and assertion infrastructure is already implemented. Before scaling this to the full suite, the structure has been reorganized as described below.

### Dedicated BOM: `browser_object_glean.py`

The current `AboutGlean` class lives in `modules/page_object_about_pages.py`. In practice, `poll_glean_metric` does not interact with the about:glean page — it executes JavaScript in the Firefox chrome context using `Services.fog.testFlushAllChildren()` and `Glean.<metric>.testGetValue()` to retrieve telemetry values.

Because this logic operates at the browser level rather than the page DOM, it fits more naturally in a Browser Object Model (BOM). The class should be moved to:

```
modules/browser_object_glean.py
```

The corresponding component JSON should explicitly declare `"context": "chrome"` at the top level.

### Separate Test Suite: `tests/glean/`

The proof-of-concept test currently lives under `tests/address_bar_and_search/`, which follows the STARfox convention of one test file per manual test case. Glean telemetry tests follow a different pattern — they use shared utilities, parametrized datasets, and cover combinations of engines, regions, and entry surfaces.

Keeping these tests in `address_bar_and_search/` would introduce unrelated preferences (`telemetry.fog.test.localhost_port`, `datareporting.healthreport.uploadEnabled`) and mix organizational patterns within the same folder.

A dedicated folder isolates telemetry configuration, datasets, and helpers:

```
tests/glean/
```

---

## Test Environment

Each automation run uses a fresh Firefox profile, which guarantees:
- No previous telemetry contamination
- Deterministic event order
- Simpler assertion logic

The following Firefox preferences are set globally for all Glean tests via `tests/glean/conftest.py`:

| Preference | Value | Purpose |
|---|---|---|
| `browser.aboutConfig.showWarning` | `False` | Suppress about:config warning |
| `datareporting.healthreport.uploadEnabled` | `True` | Enable Glean data collection |
| `telemetry.fog.test.localhost_port` | `5312` | Redirect pings to local test server |
| `browser.urlbar.scotchBonnet.enableOverride` | `True` | Enable ScotchBonnet urlbar required for SERP impression telemetry |

A `pytest-localserver` HTTP server fixture listens on `127.0.0.1:5312` to capture pings without contacting Mozilla servers.

---

## Folder Structure

The `tests/glean/` suite is organized into five subfolders, each covering a distinct Glean metric category:

```
tests/glean/
├── conftest.py                  # Shared prefs, httpserver fixture
├── flows.py                     # Entry and action dispatchers
├── utils.py                     # load_cases(__file__) helper
│
├── serp_impression/             # Glean.serp.impression         (77 cases)
│   ├── cases.json
│   └── test_serp_impression.py
│
├── serp_abandonment/            # Glean.serp.abandonment        (24 cases)
│   ├── cases.json
│   └── test_serp_abandonment.py
│
├── serp_engagement/             # Glean.serp.engagement +       (18 cases)
│   ├── cases.json               # browserEngagementNavigation
│   └── test_serp_engagement.py
│
├── serp_ad/                     # browserSearchWithads,         (13 cases)
│   ├── cases.json               # browserSearchAdclicks,
│   └── test_serp_ad.py          # browserSearchContent,
│                                # sap.searchFormCounts,
│                                # serp.adImpression
│
└── serp_sap/                    # Glean.sap.counts              (78 cases)
    ├── cases.json
    └── test_serp_sap.py
```

Total: **210 automated test cases** covering 7 search engines across all SERP telemetry metrics.

---

## Parametrized Test Design

The SERP telemetry suite covers a large number of manual TestRail cases representing combinations of:

- Search engine and region
- Search entry surface (urlbar, searchbar, contextmenu, urlbar_searchmode, etc.)
- Post-search actions (reload, tab history navigation, tab close, click ads, etc.)

While these appear as separate manual cases in TestRail, they share the same automation logic: set up the engine, perform a search, optionally apply a post-SERP action, retrieve the recorded telemetry event, and validate the payload.

### Case Schema

Every `cases.json` file follows an identical top-level schema:

```json
{
  "metric": "serp.impression",
  "cases": [
    {
      "id": "C3255425",
      "entry": "urlbar",
      "action": null,
      "params": { "engine": "Google" },
      "prefs": [["browser.search.region", "US"]],
      "expected": {
        "provider": "google",
        "partner_code": "firefox-b-1-d",
        "source": "urlbar",
        "tagged": "true"
      }
    }
  ]
}
```

| Key | Description |
|---|---|
| `metric` | Glean API to poll — top-level default, can be overridden per case |
| `id` | TestRail case ID |
| `entry` | How the user opens the SERP (urlbar, searchbar, contextmenu, …) |
| `action` | What happens after the SERP loads (null, reload, tab_close, click_ads, …) |
| `params` | Runtime inputs to the flow (engine name, flags like `is_private`) |
| `prefs` | Per-case Firefox preferences (e.g. region) |
| `expected` | Subset of fields to assert in the Glean ping |

The `expected` dict uses **subset matching** — only the specified fields are asserted. This allows the same schema to work across metric types that return different payloads.

### Entry vs Action separation

`entry` and `action` are kept as distinct keys with clear semantic boundaries:

- **`entry`** — a surface that opens the SERP: `urlbar`, `searchbar`, `contextmenu`, `urlbar_handoff`, `urlbar_searchmode`, `urlbar_persisted`, `system`, `webextension`, `about_newtab`, `about_home`, and follow-on search variants
- **`action`** — something that happens after the SERP is loaded: `reload`, `tabhistory`, `open_in_new_tab`, `tab_close`, `navigation`, `back_navigation`, `refresh_navigation`, `window_close`, `click_ads`, `click_non_ads`

`unknown` is not a flow — any case with `entry: "unknown"` is skipped with a clear reason at runtime.

### Flow Dispatch

Entry and action logic is centralised in `tests/glean/flows.py` using a decorator-based registry:

```python
@_entry("urlbar")
def _entry_urlbar(driver, search_term, params): ...

@_action("tab_close")
def _action_tab_close(driver, params): ...
```

The public API is two functions: `run_entry(driver, entry, search_term, params)` and `run_action(driver, action, params)`. Adding a new flow is one decorated function — no dispatcher logic to touch.

### Test Function Shape

Every test file follows the same structure:

```python
data = load_cases(__file__)
METRIC = data["metric"]

@pytest.fixture(params=data["cases"], ids=lambda c: c["id"])
def case(request): return request.param

@pytest.fixture()
def test_case(case): return case["id"]

@pytest.fixture()
def add_to_prefs_list(case): return [tuple(p) for p in case.get("prefs", [])]

def test_serp_*(driver, case):
    engine = case.get("params", {}).get("engine")
    if engine:
        prefs.open()
        prefs.search_engine_dropdown().select_option(engine)

    run_entry(driver, case["entry"], SEARCH_TERM, params)
    run_action(driver, case.get("action"), params)

    metric = case.get("metric", METRIC)
    events = glean.poll_glean_metric(metric)
    GleanAsserts.assert_payload(metric, events, case["expected"])
```

One pattern, five folders — no special-casing between metric types.

---

## Engines and Expected Ping Values

| Engine | Region | `provider` | `partner_code` |
|---|---|---|---|
| Google | US | `google` | `firefox-b-1-d` |
| Google | DE / CA | `google` | `firefox-b-d` |
| Bing | all | `bing` | `MOZI` |
| DuckDuckGo | all | `duckduckgo` | `ffab` |
| Ecosia | DE | `ecosia` | `mzl` |
| Qwant | FR | `qwant` | `brz-moz` |
| Perplexity | all | `perplexity` | `firefox` |
| Baidu | CN | `baidu` | — |

All ping values live inline in each `cases.json`. To update a partner code, open the relevant JSON file and change `expected.partner_code` for the affected cases — no Python logic touched.

---

## Benefits

**Reduced duplication**
Entry and action logic is implemented once in `flows.py` and reused across all 210 cases.

**Scalability**
Adding a new engine or region is one JSON entry. Adding a new flow is one decorated function.

**Easy to update**
When a partner code or provider ID changes, the update is made in `cases.json` — no Python logic touched.

**Clear traceability**
Each case carries a TestRail ID used directly by pytest as the parametrize ID and reported back via the `test_case` fixture.

**Consistent assertion**
All telemetry validations use the same `GleanAsserts.assert_payload` with subset matching, regardless of which metric is being tested.

---

## Infrastructure Gaps

The following items are needed to implement the flows beyond `urlbar`:

| Item | Needed for |
|---|---|
| `searchbar` entry — add search bar via Customize, type and press Enter | `serp_impression`, `serp_ad`, `serp_sap` |
| `contextmenu` entry — select text, right-click → Search | `serp_impression`, `serp_sap` |
| `contextmenu_visual` entry — right-click image → visual search | `serp_impression`, `serp_sap` |
| `urlbar_handoff` entry — type in new tab search box | `serp_impression`, `serp_sap` |
| `urlbar_searchmode` entry — click USB, pick engine, search | `serp_impression`, `serp_sap` |
| `urlbar_persisted` entry — search, then refine in urlbar | `serp_impression`, `serp_sap` |
| `reload` action — reload the SERP tab | `serp_impression` |
| `tabhistory` action — navigate away then Back | `serp_impression` |
| `open_in_new_tab` action — middle-click / Ctrl+click SERP result | `serp_impression` |
| `tab_close`, `navigation`, `back_navigation`, `refresh_navigation`, `window_close` actions | `serp_abandonment` |
| `click_non_ads`, `click_ads` actions — click organic / sponsored SERP results | `serp_engagement` |
| `GleanAsserts` UUID presence check for `impression_id` | `serp_abandonment` |
| `__present__` sentinel handling in `assert_payload` | `serp_ad` (`serp.adImpression`) |

---

## TestRail Reporting

TBD
