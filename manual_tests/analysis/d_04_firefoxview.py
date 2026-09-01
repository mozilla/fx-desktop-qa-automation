from _ledger import C

# ---------------------------------------------------------------- suite 42945
# "about:firefoxview" (180 cases). Tree: browser/components/firefoxview/tests/browser/ = 28 tests.
# NOTE: this manual suite is unusually design/a11y-heavy - roughly half of its cases are
# "displayed according to design / figma / HCM / themes / screen reader / zoom / HiDPI",
# which browser-chrome never asserts. Those stay manual.
C(
    42945,
    "STRONG",
    "browser/components/firefoxview/tests/browser/browser_firefoxview.js; browser_firefoxview_navigation.js; "
    "browser_reload_firefoxview.js; browser_firefoxview_paused.js",
    "The about:firefoxview page itself: loads, the category navigation works, and the view "
    "pauses/resumes correctly.",
    [2224708],
)
C(
    42945,
    "STRONG",
    "browser/components/firefoxview/tests/browser/browser_firefoxview_tab.js; browser_entrypoint_management.js",
    "The Firefox View button in the tab strip: present, pin/unpin from the overflow menu, and "
    "removal / move via Customize.",
    [2283992, 2284129, 2284130],
)
C(
    42945,
    "STRONG",
    "browser/components/firefoxview/tests/browser/browser_opentabs_firefoxview.js; browser_opentabs_cards.js; "
    "browser_opentabs_changes.js; browser_opentabs_more.js; "
    "browser/components/tabbrowser/test/browser/tabs/browser_exclude_fxview_hidden_tabs.js",
    "Open Tabs card: one card per window, list order mirrors the tab strip, live updates when "
    "tabs open/close, the 5-item cap in Recent Browsing, Show More / Show Less, hidden tabs excluded.",
    [2224488, 2224490, 2224491, 2223233, 2224638, 2224639, 2510940],
)
C(
    42945,
    "STRONG",
    "browser/components/firefoxview/tests/browser/browser_opentabs_recency.js",
    "Sorting Open Tabs by recency vs by tab-strip order, including after tabs are moved and "
    "across multiple windows.",
    [2498481, 2498482, 2498483, 2483400, 2483424],
)
C(
    42945,
    "STRONG",
    "browser/components/firefoxview/tests/browser/browser_opentabs_pinned_tabs.js; "
    "browser/components/firefoxview/tests/browser/browser_firefoxview_dragDrop_pinned_tab.js",
    "Pinned tabs in the Open Tabs section, across multiple windows, and pin/unpin driven from "
    "the tab strip.",
    [2482613, 2483389, 2483396],
)
C(
    42945,
    "STRONG",
    "browser/components/firefoxview/tests/browser/browser_opentabs_tab_indicators.js; browser_opentabs_tab_favicons.js",
    "The row indicators: pinned, bookmarked, media/sound, container - including the bookmark "
    "indicator appearing and disappearing as bookmarks change.",
    [2483398, 2483405, 2483805, 2483806, 2498485, 2498493, 2498616, 2498853, 2498854],
)
C(
    42945,
    "STRONG",
    "browser/components/firefoxview/tests/browser/browser_history_firefoxview.js",
    "History card: entry point, sort by date vs by site, day/site grouping, delete an entry, "
    "and opening an entry.",
    [2224640, 2224642, 2224691, 2224694, 2224706],
)
C(
    42945,
    "STRONG",
    "browser/components/firefoxview/tests/browser/browser_recentlyclosed_firefoxview.js; "
    "browser/components/sessionstore/test/browser_forget_closed_tab_window_byId.js",
    "Recently Closed card: 25-item cap, empty state, dismissing an item, and a dismissed item no "
    "longer being reachable via Ctrl+Shift+T.",
    [2230465, 2230467, 2303062, 2303063],
)
C(
    42945,
    "STRONG",
    "browser/components/firefoxview/tests/browser/browser_syncedtabs_firefoxview.js; "
    "browser_syncedtabs_errors_firefoxview.js",
    "Tabs From Other Devices: the page itself with a signed-in account, plus every degraded state "
    "(sync service down, offline, primary password locked, disabled by policy, sync-open-tabs "
    "unchecked, account disconnected).",
    [2231506, 2224482, 2224479, 2224480, 2224481, 2283845, 2284746, 2284747],
)
C(
    42945,
    "STRONG",
    "browser/components/firefoxview/tests/browser/browser_opentabs_search.js; browser_firefoxview_search_telemetry.js",
    "Search across Recent Browsing / Open Tabs / Recently Closed / Tabs From Other Devices / "
    "History by title and URL, and the no-results message.",
    [2421681, 2421682, 2421683, 2421684, 2421685, 2421689],
)
C(
    42945,
    "STRONG",
    "browser/components/firefoxview/tests/browser/browser_firefoxview_virtual_list.js",
    "Virtualised list stability with a large number of open/recently-closed tabs.",
    [2421704],
)
C(
    42945,
    "STRONG",
    "browser/components/firefoxview/tests/browser/browser_tab_list_keyboard_navigation.js",
    "Keyboard-only navigation of the tab lists and their row indicators.",
    [2421690, 2483403, 2498861],
)
C(
    42945,
    "STRONG",
    "browser/components/firefoxview/tests/browser/browser_firefoxview_general_telemetry.js; "
    "browser_firefoxview_search_telemetry.js",
    "The Firefox View Glean/telemetry event set: entry-point click, page load, card "
    "collapse/expand, view-all clicks, item-menu clicks, dismiss, sort, sign-in CTAs, "
    "history-item clicks, search.",
    [2288333, 2288334, 2288335, 2288336, 2288337, 2288338, 2288339, 2288340, 2288341,
     2298243, 2298245, 2314926, 2303048, 2303049, 2314578, 2298241, 2298242, 2298253,
     2308023, 2298246, 2298247, 2298248, 2298251, 2298252, 2315378, 2308019, 2308021],
)
C(
    42945,
    "MEDIUM",
    "browser/components/firefoxview/tests/browser/browser_firefoxview.js; browser_opentabs_cards.js; "
    "browser_dragDrop_after_opening_fxViewTab.js; browser_tab_close_last_tab.js; browser_tab_on_close_warning.js; "
    "browser_chats_firefoxview.js",
    "Card collapse/expand, empty states, Show-All-to-Library, the item three-dot menu, "
    "send-to-device and the close-warning are touched in-tree but not asserted the way the manual "
    "cases describe. Everything design/figma/HCM/theme/zoom/HiDPI/screen-reader in this suite has "
    "no in-tree analog at all.",
    [2221364, 2223229, 2223230, 2223231, 2223232, 2224468, 2224471, 2224473, 2224475,
     2224486, 2224489, 2224630, 2224632, 2224634, 2224635, 2224502, 2303066, 2303068,
     2308857, 2224641, 2224689, 2224692, 2224693, 2224695, 2224696, 2224697, 2224699,
     2224700, 2230464, 2230469, 2232659, 2232660, 2284320, 2284745, 2284131, 2284132,
     2284133, 2285176, 2339636, 2421686, 2455843, 2421687, 2421688, 2421691, 2421692,
     2421693, 2421694, 2421695, 2421696, 2421697, 2483390, 2483397, 2483399, 2483407,
     2483425, 2483426, 2483808, 2483809, 2510939, 2510941, 2524916, 2525302, 2498872,
     2498484, 2498621, 2498622, 2498851, 2498852, 2498856, 2498857, 2498858, 2498476,
     2498864],
)
