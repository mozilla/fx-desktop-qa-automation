"""Append Part 5 to FIREFOX_TEST_COVERAGE_COMPARISON.md."""

import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

part5 = open(os.path.join(HERE, "summary.md"), encoding="utf-8").read().strip()

BODY = """

---
---

# Part 5 - Manual cases with STRONG in-tree automated coverage (low-priority candidates)

> **Purpose (per request):** the deliverable here is a **per-case list** - exact TestRail case id,
> title, suite and section - of manual cases whose user flow is already driven end-to-end by
> automated tests **inside `mozilla-firefox/firefox`**. The intent is for the manual team to mark
> these low priority so they can be skipped during crunch time.
>
> **Generated:** 2026-07-31. Parts 1-4 compared at *suite / feature-area* level; Part 5 is the
> *case-level* pass.
>
> **Machine-readable output:** [`manual_tests/LOW_PRIORITY_CANDIDATES.csv`](manual_tests/LOW_PRIORITY_CANDIDATES.csv)
> - **2,686 rows**, columns `case_id, title, suite_id, suite_name, section_id, priority_id,
> already_automated_in_starfox, in_tree_tests, why`. Import straight into TestRail and bulk-set
> priority.
>
> **Verdict ledger:** `manual_tests/analysis/d_*.py` - 312 clusters, each holding the tree test
> paths, the rationale and the case ids. Re-run `python manual_tests/analysis/build_report.py`
> to regenerate the CSV after any edit.

## 5.1 Method (what changed vs Parts 1-4)

1. **The tree inventory was pulled live, not recalled.** Recursive git trees for 15 top-level
   subtrees of `mozilla-firefox/firefox` @ `7d438b9` (2026-07-30) gave **89,541 files**, of which
   **8,762 are browser-chrome `browser_*.js` tests**. Cached under `.fxtree/` with a query helper.
2. **Candidate pool:** the 4,619 manual cases in the 29 suites Part 3 classified STRONG.
3. **Per-case verdict**, two tiers:
   - **STRONG** - an in-tree test drives the same UI flow and asserts the same user-visible
     outcome. Goes in the CSV.
   - **MEDIUM** - the tree touches the feature but at narrower scope or lower altitude
     (pref-only, telemetry-only, one variant of a matrix). Stays in the manual rotation.
4. **File contents were read, not just filenames**, wherever a mapping was not 1:1 or covered many
   manual cases. This caught real errors - see SS5.4.

## 5.2 Results by suite

{TABLE}

**Read:** across the 29 reviewed suites, **2,686 of 4,619 cases (58%)** have a genuine in-tree
counterpart and are safe to de-prioritise. **283 of them are *also* already automated in STARfox**
(`custom_automation_status = 4`) - those are doubly redundant and should be the first to go.

## 5.3 The four big wins

Roughly half the list is concentrated in four places. Each is a **repetition matrix**: one mechanic
that the tree automates once, repeated many times manually across engines, regions, file types,
form fields or platforms.

| # | What | Cases | In-tree counterpart | Recommendation |
|---|---|---:|---|---|
| 1 | **SAP search-count telemetry** (Address Bar sec. 617205) - engine x region x source x follow-on | **393** | `browser/components/search/test/browser/telemetry/` (59 tests) covers every source: urlbar, searchbar, websearch bar, context menu, newtab, reload, tabhistory, ad impressions, ad clicks, abandonment | Keep **one engine x region x source triple per engine** as a smoke check; de-prioritise the other ~370. The counting mechanic is automated - only the *real per-region partner code* is genuinely manual. |
| 2 | **File-type handler matrix** (Downloads sec. 284144) - "add `.<ext>` to Firefox" x 110 extensions | **126** | `preferences/tests/applications/` + `downloads/browser_downloads_handle_new_file_types.js` + `uriloader/exthandler/.../browser_download_preferred_action.js` | Keep **3 representatives** (one executable, one archive, one media). |
| 3 | **Unified autocomplete per-field matrix** (Form Autofill sec. 542292-542301, 580065-580067) | **73** | `formautofill/test/browser/` (157 tests) covers dropdown composition, preview, fill, highlight, clear and the footer generically across all detected field types | Keep **one field per section**. |
| 4 | **Onboarding platform matrix** (Easy Setup sec. 439115-439184) - same 11 slides x ~5 platform blocks | **83** | `aboutwelcome/tests/browser/` - a dedicated test per slide (multistage MR, multiselect, language switcher, import, mobile QR, AMO picker, gratitude) | Keep **one platform block**; retain the pinned/default-browser permutations, which are OS state the tree cannot set. |

**Plus one pure duplicate:** suite **103289 "Onboarding" (75 cases)** repeats suite 70279's Smart
Window cases almost verbatim. That is a de-duplication problem independent of automation coverage -
worth resolving in TestRail regardless.

## 5.4 Corrections to Parts 1-4 found by reading the tests

Verifying file *contents* rather than filenames overturned four earlier calls:

| Earlier claim | Reality |
|---|---|
| Suite **1977** = "PDF viewer pdf.js", STRONG (sec. 3.11) | It is a **graphics / rendering / site-compat** suite (WebGL, canvas, ClearType, hardware acceleration). Reclassify **WEAK**; excluded from this pass. |
| pdf.js well covered in-tree | **Much thinner than the filenames suggest.** `browser_pdfjs_form.js` only asserts the `renderInteractiveForms` pref - it never fills a field. `browser_pdfjs_comment.js` only checks a "learn more" URL. So ~90 manual PDF form-field and commenting cases have **no** in-tree counterpart (they are covered upstream in `github.com/mozilla/pdf.js`, a different repo). Suite 65 drops to 8 STRONG cases out of 196. |
| Local Network Access - no coverage found under `browser/` | It lives in **`netwerk/test/browser/`** - 11 LNA browser-chrome tests. `browser_test_local_network_access_permissions.js` drives the real doorhanger: allow, deny, remembered-within-expiry, re-prompt after expiry. |
| Terms of Use onboarding assumed covered with the rest of onboarding | **No in-tree test exists.** Searching the whole tree for `termsofuse`/`TermsOfUse` returns only `browser/locales/en-US/browser/termsofuse.ftl`. Suite 59371 keeps 69 of its 75 cases manual. |

## 5.5 Two housekeeping findings

1. **9 duplicated rows in the export.** These case ids appear twice in `all_cases.json`:
   `135195, 429868, 563508, 1746418, 2246549, 3029243, 3180065, 3898142, 4028081`.
   Worth de-duplicating in TestRail.
2. **Cases already tagged for removal.** Address Bar section **665881** (6 cases) is explicitly
   titled `[to remove]` / `[review/remove]` / `[duplicate]` / `[TO BE REMOVED]` by the manual team.
   Retire rather than re-triage. Same for the **102 Shopping / Review Checker** cases (feature
   removed from the tree in 2025) already flagged in sec. 3.7.

## 5.6 What deliberately stays manual

The 994 MEDIUM cases plus everything outside the reviewed pool. The recurring reasons, in rough
order of volume:

- **Visual / design conformance** - Figma specs, themes, High Contrast, RTL builds, HiDPI,
  zoom levels, window-resize layout. browser-chrome asserts control *behaviour*, never appearance.
  This is most of the redesigned-Settings, NOVA and Firefox View sections.
- **Assistive technology** - NVDA / VoiceOver / Orca. The tree tests the a11y *tree and API*, not
  a real screen reader.
- **Real sites and live accounts** - the 45-site password-manager matrix, the 45-site
  password-generation matrix, live FxA sign-in / 2FA / recovery flows, live Sync, real DRM.
- **OS integration** - installers, taskbar pinning, PIN/fingerprint OS auth, file pickers,
  the Windows DLP agent, Family Safety.
- **Not Firefox code at all** - ~70 Security & Privacy cases test the *Firefox Monitor website*
  and its Bento menu. These should arguably move out of the desktop suite entirely.

## 5.7 Caveats

- Point-in-time snapshot of `main` @ `7d438b9` (2026-07-30). The tree moves; re-run
  `build_report.py` against a fresh `.fxtree/` before a release cycle.
- "STRONG" means *the same user flow is asserted somewhere in the tree*, not that the assertions
  are identical. A manual case may still catch a regression its in-tree counterpart misses.
- De-prioritising is not deleting. The recommendation is *skip during crunch time*, not retire -
  except for the explicitly-flagged sections in sec. 5.5.
"""

doc = os.path.join(ROOT, "FIREFOX_TEST_COVERAGE_COMPARISON.md")
with open(doc, "a", encoding="utf-8") as fh:
    fh.write(BODY.replace("{TABLE}", part5))
print("appended Part 5 to", doc)
