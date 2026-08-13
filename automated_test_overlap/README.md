# Automated STARfox tests ↔ Firefox tree overlap (round 5)

Rounds 1–4 asked whether **manual** TestRail cases were already covered by automation in
[mozilla-firefox/firefox](https://github.com/mozilla-firefox/firefox). This round turns the
question on the automation itself:

> For each **automated STARfox test**, does the Firefox tree already have a test that drives
> the same flow and asserts the same outcome?

That is a sharper comparison than the earlier rounds could make, because both sides are real
code. The STARfox test is in this repo and can be read directly, rather than inferred from a
manual case's prose.

## Headline

**281 of 349 automated STARfox tests (81%) are duplicated by an in-tree test.**

| | STARfox tests | TestRail cases |
|---|---:|---:|
| **STRONG** — an in-tree test drives the same flow and asserts the same outcome | **281** (81%) | 301 |
| **PARTIAL** — the tree covers part of it; the STARfox test still earns its place | 37 (11%) | 101 |
| **UNIQUE** — nothing in the tree covers this; STARfox is the only automated coverage | 31 (9%) | 33 |

## Population

Selected from `manual_tests/all_cases.json` on `custom_automation_coverage` in (2, 3) — the
TestRail field recording a case as covered by STARfox automation — at **any** priority:

| | Count |
|---|---:|
| Cases marked as STARfox-covered | 519 |
| ... of which `custom_automation_coverage: 3` (Full) | 515 |
| ... `custom_automation_coverage: 2` (Partial) | 4 |
| Distinct STARfox test files they name | **349** |
| Cases with no usable test name | 84 |
| Cases naming a test that no longer exists | 7 |

457 of the 519 cases carry a `custom_automated_test_names` value, which is what makes the
test-level comparison possible. Cases are referred to by their TestRail number — `C` plus the
export's `id`, e.g. **C2241112**.

## Outputs

| File | Contents |
|---|---|
| `STARFOX_TREE_OVERLAP.csv` | One row per STARfox test: verdict, the TestRail cases it covers, the in-tree tests, and the rationale. |
| `STARFOX_TREE_OVERLAP_cases.csv` | One row per TestRail case, for filtering on the TestRail side. |
| `analysis/summary.md` | The per-suite table below. |
| `analysis/housekeeping.md` | Dead TestRail→STARfox links, cases with no test name, and STARfox tests no case points at. |

## Results by STARfox suite

| STARfox suite | Tests | STRONG (duplicated) | % | PARTIAL | UNIQUE |
|---|---:|---:|---:|---:|---:|
| tests/security_and_privacy | 60 | **51** | 85% | 9 | 0 |
| tests/password_manager | 46 | **36** | 78% | 7 | 3 |
| tests/address_bar_and_search | 37 | **31** | 84% | 3 | 3 |
| tests/bookmarks_and_history | 27 | **25** | 93% | 2 | 0 |
| tests/tabs | 25 | **25** | 100% | 0 | 0 |
| tests/form_autofill | 19 | **19** | 100% | 0 | 0 |
| tests/downloads | 19 | **12** | 63% | 7 | 0 |
| tests/notifications | 13 | **12** | 92% | 0 | 1 |
| tests/sidebar | 24 | **12** | 50% | 1 | 11 |
| tests/pdf_viewer | 20 | **10** | 50% | 2 | 8 |
| tests/preferences | 8 | **7** | 88% | 1 | 0 |
| tests/audio_video | 6 | **6** | 100% | 0 | 0 |
| tests/menus | 7 | **6** | 86% | 1 | 0 |
| tests/networking | 6 | **6** | 100% | 0 | 0 |
| tests/scrolling_panning_zooming | 5 | **5** | 100% | 0 | 0 |
| tests/session_restore | 5 | **5** | 100% | 0 | 0 |
| tests/find_toolbar | 3 | **3** | 100% | 0 | 0 |
| tests/geolocation | 2 | **2** | 100% | 0 | 0 |
| tests/language_packs | 2 | **2** | 100% | 0 | 0 |
| tests/printing_ui | 2 | **2** | 100% | 0 | 0 |
| tests/reader_view | 3 | **2** | 67% | 1 | 0 |
| tests/theme_and_toolbar | 2 | **2** | 100% | 0 | 0 |
| tests/drag_and_drop | 5 | **0** | 0% | 0 | 5 |
| tests/glean/serp_abandonment | 1 | **0** | 0% | 1 | 0 |
| tests/glean/serp_impression | 1 | **0** | 0% | 1 | 0 |
| tests/profile | 1 | **0** | 0% | 1 | 0 |
| **Total** | **349** | **281** | **81%** | **37** | **31** |

## Where STARfox is redundant

Six suites are at or near 100% duplicated. In each case the tree has a directory that maps
almost one-to-one onto the STARfox suite:

| STARfox suite | In-tree counterpart | Tree tests |
|---|---|---:|
| tests/form_autofill | `browser/extensions/formautofill/test/browser/` (+ `creditCard/`, `address/`) | 55 |
| tests/password_manager | `browser/components/aboutlogins/tests/browser/` + `toolkit/components/passwordmgr/test/browser/` | 29 + 33 |
| tests/tabs | `browser/components/tabbrowser/test/browser/tabs/` + `tabMediaIndicator/` | 196 + 14 |
| tests/address_bar_and_search | `browser/components/urlbar/tests/` (15 subdirectories) | 354 |
| tests/security_and_privacy | `browser/base/content/test/protectionsUI/` + `privatebrowsing/` + `siteIdentity/` | 24 + 45 + 35 |
| tests/networking | `toolkit/components/doh/test/browser/` | 14 |

The urlbar comparison is the most lopsided: `browser-searchMode/` alone has 29 tests, more
than the entire STARfox search-mode group it duplicates.

## Where STARfox is the only automated coverage

The 31 UNIQUE tests concentrate in four places, and they are worth protecting:

- **Vertical tabs (11 tests, tests/sidebar).** The largest block of genuinely unique coverage.
  `browser/components/sidebar/tests/browser/` has 51 tests, but they treat the open-tabs panel
  as a read-only list. Duplicating a vertical tab, reloading one, bookmarking it, muting it, its
  close and move submenus, multi-select and multi-select close, reopening a closed vertical tab,
  pinning with expand-on-hover on, and switching between horizontal and vertical layouts have no
  in-tree counterpart at all.
- **PDF form interaction (8 tests, tests/pdf_viewer).** Typing into text and numeric fields,
  editing pre-filled values, dropdowns, checkboxes, and zoom behaviour inside fields.
  `toolkit/components/pdfjs/test/browser_pdfjs_form.js` only asserts the form is fillable at
  all; the per-widget behaviour lives upstream in mozilla/pdf.js, outside the tree being
  compared.
- **Cross-application clipboard (5 tests, tests/drag_and_drop).** Copying table rows, columns,
  headers and hyperlinked cells into and out of third-party editors. In-tree clipboard tests
  never leave Firefox.
- **Live partner and endpoint contracts (7 tests, spread).** Bing and DuckDuckGo search codes,
  DuckDuckGo telemetry, the password manager against google.com / reddit.com / facebook.com, and
  geolocation against a live endpoint. The tree does not test against the live web by design, so
  these are the only automated defence against a real site or partner contract changing.

## The Glean SERP tests are the one ambiguous case

`tests/glean/serp_impression` and `tests/glean/serp_abandonment` are two test files but 65
TestRail cases, each parametrized over a matrix in a sibling `cases.json`: 9 entry points × 5
real engines for impressions, 3 abandonment actions for the other.

The tree covers the *mechanic* thoroughly — `browser_search_telemetry_abandonment.js` has a task
per action and asserts the same payload; the `sources_*` tests cover every entry point. But all
of them run against a fabricated SERP at
`example.org/browser/browser/components/search/test/browser/telemetry/searchTelemetry.html`
with a provider regex defined inside the test.

What the STARfox matrix adds is the half a mock cannot reach: that each *real* engine's live
markup is still matched by the shipped remote-settings selectors, and that the event carries the
right `provider` and `partner_code` (e.g. `firefox-b-1-d`). That is why the test file ships a
`BOT_CHALLENGE_SKIPS` table for engines that serve a challenge to CI IPs.

Verdict: PARTIAL, not STRONG. The schema is duplicated; the live-engine and partner-code
coverage is not.

## Housekeeping findings

Three data-quality problems fall out of the link resolution — see `analysis/housekeeping.md`:

1. **7 cases point at a STARfox test that no longer exists.** One is a clear rename that
   TestRail never picked up: C3028773 names
   `test_seach_suggestions_can_be_disabled.py` (note the typo), while the corrected
   `test_search_suggestions_can_be_disabled.py` sits in the repo with no case pointing at it.
2. **84 cases are marked STARfox-covered but name no test.** They cannot be verified either
   way, and they inflate the apparent automation coverage.
3. **46 STARfox tests have no TestRail case pointing at them.** Some are meta/harness tests, but
   the rest are running in CI with no case recording that they exist — including
   `test_search_code_google_us.py` and `test_search_code_google_non_us.py`, which look like
   partner-code coverage of the same kind flagged as UNIQUE above.

## Method

Same tiering shape as rounds 1–4, but keyed by STARfox test rather than manual case.

```bash
python manual_tests/analysis/fetch_tree.py              # refresh the .fxtree inventory first

python automated_test_overlap/analysis/sheet.py         # overview
python automated_test_overlap/analysis/sheet.py tests/tabs --titles
python automated_test_overlap/analysis/sheet.py --orphans
python automated_test_overlap/analysis/build_report.py  # CSVs + summary + housekeeping
python automated_test_overlap/analysis/validate.py      # check every cited tree path
```

| File | Role |
|---|---|
| `analysis/pop.py` | Population, and resolution of `custom_automated_test_names` onto real repo files. |
| `analysis/ledger.py` | `T()` records a verdict for one or more STARfox tests; `TDIR()` / `TREST()` take a whole directory. `T()` fails at import time if a STARfox path does not exist. |
| `analysis/a_01_*.py` … `a_06_*.py` | The analysis, as data. |
| `analysis/build_report.py` | Writes both CSVs, `summary.md` and `housekeeping.md`. Fails loudly on a test claimed by two clusters. |
| `analysis/validate.py` | Checks every cited tree path against the inventory. **504 distinct paths, 0 unverified.** |

## Caveats

- Point-in-time snapshot of `main` @ `5069177` (2026-08-12). Re-run `fetch_tree.py`,
  `validate.py` and `build_report.py` before acting on this later.
- STRONG means *the same flow is asserted somewhere in the tree*, not that the assertions are
  identical. A STARfox test can still catch a regression its in-tree counterpart misses —
  notably, many STARfox tests drive **live external URLs** where the in-tree tests use a local
  server, so they exercise real network and real markup.
- Deleting a STRONG test is a bigger decision than de-prioritising a manual case. The useful
  reading is: **stop adding new STARfox tests in these areas**, and treat the 281 as the first
  place to look when the suite needs to get faster or a test goes flaky. The 31 UNIQUE tests are
  the opposite — they are the suite's real value and should be kept green.
- Coverage in the tree only grows, so a stale snapshot understates duplication rather than
  overstating it.
