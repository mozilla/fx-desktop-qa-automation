"""Round 5 -- tests/glean/serp_impression and tests/glean/serp_abandonment.

Two STARfox test files, but 65 linked TestRail cases: both are parametrized over a matrix
loaded from a sibling cases.json.

  serp_impression   50 cases -- 9 entry points (urlbar, searchbar, contextmenu,
                    urlbar_handoff, urlbar_persisted, urlbar_searchmode, contextmenu_visual,
                    follow_on_from_refine_on_incontent_search, unknown) x 5 engines
                    (Google, Bing, DuckDuckGo, Ecosia, Qwant)
  serp_abandonment  25 cases -- tab_close / navigation / window_close x the same engines

This is the one place in the comparison where the overlap is genuinely ambiguous, so it is
worth being precise about.

The tree covers the *mechanic* thoroughly. browser_search_telemetry_abandonment.js has a task
per abandonment action, the sources tests cover the entry-point attribution, and
browser_search_telemetry_impressionAttributes.js covers the impression payload. But every one
of those runs against a fabricated SERP served from
example.org/browser/browser/components/search/test/browser/telemetry/searchTelemetry.html with a
provider regex defined inside the test.

What the STARfox matrix adds is the half that a mock cannot reach: that each *real* engine's
live markup is still matched by the shipped remote-settings selectors, and that the resulting
event carries the right `provider` and `partner_code` (e.g. `firefox-b-1-d` for Google). Those
are partner-contract assertions against live pages -- which is also why the test file carries a
BOT_CHALLENGE_SKIPS table for engines that serve a challenge to CI IPs.

So: PARTIAL, not STRONG. The event schema is duplicated; the live-engine and partner-code
coverage is not.
"""

from ledger import T

TEL = "browser/components/search/test/browser/telemetry/"

T(
    "PARTIAL",
    TEL + "browser_search_telemetry_impressionAttributes.js; "
    "browser_search_telemetry_sources.js; browser_search_telemetry_sources_navigation.js; "
    "browser_search_telemetry_sources_in_content.js; "
    "browser_search_telemetry_sources_webextension.js; "
    "browser_search_glean_serp_event_telemetry_categorization_enabled_by_pref.js",
    "The serp.impression event and its source attribution are covered in tree for every entry "
    "point this matrix walks -- urlbar, searchbar, in-content follow-on, webextension, unknown -- "
    "but against a fabricated SERP with a test-local provider regex. The 5-engine dimension and "
    "the provider / partner_code assertions against live engine markup have no in-tree "
    "equivalent, and cannot have one.",
    ["tests/glean/serp_impression/test_serp_impression.py"],
)
T(
    "PARTIAL",
    TEL + "browser_search_telemetry_abandonment.js; "
    "browser_search_telemetry_engagement_content.js; "
    "browser_search_telemetry_engagement_multiple_tabs.js",
    "browser_search_telemetry_abandonment.js has a dedicated task for each action this matrix "
    "parametrizes -- test_tab_close_before_page_load, test_tab_close_after_page_load, "
    "test_window_close, test_navigation_via_urlbar, test_navigation_via_back_button -- and "
    "asserts the same abandonment payload. Again the gap is the live-engine dimension rather "
    "than the mechanic.",
    ["tests/glean/serp_abandonment/test_serp_abandonment.py"],
)
