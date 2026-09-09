from _ledger import C, CSEC

# ---------------------------------------------------------------- suite 65334
# "Address Bar 138+" (1068 cases) - the largest manual suite in the corpus.
# Tree: browser/components/urlbar/tests/ = ~420 browser-chrome tests across 20
# sub-directories (browser/, browser-autofill/, browser-editing/, browser-results/,
# browser-search/, browser-searchMode/, browser-tabs/, browser-tips/, browser-UrlbarInput/,
# browser-UrlbarView/, browser-updateResults/, browser-engagementTelemetry/,
# browser-quickactions/, browser-telemetry/, browser-trustPanel/, searchbar/,
# quicksuggest/browser/) plus browser/components/search/test/browser/ (36) and
# .../telemetry/ (59). This is the most heavily automated feature area in Firefox.

# =============================================================== section 617205
# SAP / search-count telemetry matrix (393 cases = 37% of the suite).
CSEC(
    65334,
    "STRONG",
    "browser/components/search/test/browser/telemetry/browser_search_telemetry_sources.js; "
    "browser_search_telemetry_sources_ads.js; browser_search_telemetry_sources_ads_clicks.js; "
    "browser_search_telemetry_sources_in_content.js; browser_search_telemetry_sources_navigation.js; "
    "browser_search_telemetry_sources_webextension.js; browser_search_telemetry_searchbar.js; "
    "browser_search_telemetry_searchform.js; browser_search_telemetry_content.js; "
    "browser_search_telemetry_app_provided_and_overridden.js; browser_search_telemetry_adImpression_component.js; "
    "browser_search_telemetry_engagement_content.js; browser_search_telemetry_engagement_non_ad.js; "
    "browser_search_telemetry_new_window.js; browser_search_telemetry_private.js; "
    "browser_search_telemetry_post_engine.js; browser_search_telemetry_abandonment.js; "
    "browser/components/urlbar/tests/browser-engagementTelemetry/ (40 tests)",
    "MATRIX: this entire section is one mechanic - 'a SAP search from source X records a search "
    "count' - repeated across ~15 engines x ~25 regions x 8 sources (urlbar, searchbar, websearch "
    "bar, context menu, newtab, reload, tabhistory, unknown) plus follow-on-search and "
    "organic/non-organic variants. Every source and every follow-on/ad-impression/ad-click path is "
    "automated in-tree with 59 dedicated telemetry tests, and STARfox automates the partner-code "
    "checks for the main engines. What is genuinely manual-only is verifying the REAL per-region "
    "partner code against the live engine - not the counting mechanic. "
    "Recommendation: this is the single biggest crunch-time saving in the corpus. Keep one "
    "engine x region x source triple per engine as a smoke representative and de-prioritise the "
    "other ~370.",
    [617205],
)

# =============================================================== section 617190 (382)
C(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/browser-searchMode/browser_searchModeSwitcher_basic.js; "
    "browser_searchModeSwitcher_searchMode.js; browser_searchModeSwitcher_keyNavigation.js; "
    "browser_searchModeSwitcher_emptyInput.js; browser_searchModeSwitcher_appProvidedEngines.js; "
    "browser_searchModeSwitcher_dynamicUnifiedSearchButton.js; browser_searchModeSwitcher_opensearchInstall.js; "
    "browser_searchModeSwitcher_newBadge.js; browser_searchModeSwitcher_telemetry.js; browser_indicator.js; "
    "browser_indicator_clickthrough.js; browser_oneOffButton.js; browser_switchTabs.js; browser_engineRemoval.js; "
    "browser_alias_replacement.js; browser_no_results.js; browser_excludeResults.js; browser_pickResult.js; "
    "browser_sessionStore.js",
    "The Unified Search Button / search mode: entering and exiting search mode, the Bookmarks / "
    "Tabs / History modes, keyword and alias entry, switching engines mid-query, search mode "
    "surviving a tab switch, mode cleared when the engine is removed, keyboard operation, "
    "installing an engine from the button, and private-window behaviour.",
    [3028714, 3028715, 3028722, 3028723, 3028727, 3028730, 3028732, 3028905, 3029206,
     3029380, 3029381, 3029383, 3029384, 3029385, 3029386, 3029387, 3029392, 3029394,
     3029395, 3028837, 3028841, 3028842, 3028843, 3028844, 3028848, 3028850, 3028851,
     3028824],
)
C(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/browser-autofill/browser_inputHistory.js; browser_inputHistory_autofill.js; "
    "browser_inputHistory_emptystring.js; browser_originToAdaptive.js; browser_adaptive_origin_fallback.js; "
    "browser_typed.js; browser_preserve.js; browser_undo.js; browser_backspaced.js; browser_backspace_dismissal.js; "
    "browser_backspace_dismissal_guards.js; browser_backspace_dismissal_reintegration.js; browser_firstResult.js; "
    "browser_caretNotAtEnd.js; browser_clear_properly_on_accent_char.js; browser_trimURLs.js; browser_paste.js; "
    "browser_placeholder.js; browser_resultMenu_dismissal.js; browser_inputField_contextmenu_dismissal.js",
    "Adaptive-history autofill in full: entries autofilled, removal via Remove-from-History / "
    "Forget-about-this-site / Forget, use-count and frecency prioritisation, protocol and www "
    "handling, case insensitivity, the 'cheat sheet' path/prefix precedence rules, bookmark-backed "
    "autofill, and the private-browsing isolation rules.",
    [3029070, 3029071, 3029073, 3029076, 3029077, 3029078, 3029079, 3029081, 3029082,
     3029083, 3029085, 3029086, 3029087, 3029088, 3029089, 3029090, 3029091, 3029092,
     3029093, 3029094, 3029095, 3029098, 3029099, 3028888, 3029036],
)
C(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/browser-editing/browser_copying.js; browser_copy_and_paste_first_result.js; "
    "browser_cutting.js; browser_delete.js; browser_deleteAllText.js; browser_pasteAndGo.js; browser_paste_multi_lines.js; "
    "browser_removeUnsafeProtocolsFromURLBarPaste.js; browser_caret_position.js; browser_cursor.js; "
    "browser_selectionKeyNavigation.js; browser_urlbar_selection.js; browser_less_common_selection_manipulations.js; "
    "browser_ime_composition.js; browser_decode.js; browser_percent_encoded.js; browser_lossless_encode.js; "
    "browser_urlbar_contextmenu.js; browser_revert.js; browser_restoreEmptyInput.js; browser_typed_value.js; "
    "browser_userTypedValue.js; browser_edit_completed.js",
    "Address-bar text editing: copy (with the https prefix retained), cut, paste, Paste and Go, "
    "unsafe-protocol stripping on paste, drag-and-drop within the bar, double-click word selection, "
    "Shift+arrow selection, caret position across focus changes, IME composition, and the "
    "context menu.",
    [3028712, 3028883, 3028884, 3029264, 3029265, 3029421, 3029422, 3029423, 3028706,
     3028899, 3028886, 3028897, 3028893, 3028971],
)
C(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/browser-UrlbarInput/browser_trimURLs.js; browser_untrimOnUserInteraction.js; "
    "browser_formatValue.js; browser_formatValue_strikeout.js; browser_registrableDomainInView.js; "
    "browser_overflow.js; browser_overflow_resize.js; browser_setURI.js; browser_breakout_state.js",
    "URL trimming and untrim-on-interaction, the www. prefix rules, domain highlighting, and the "
    "untrimmed-http display combinations.",
    [3028781, 3029420, 3029426, 3029427, 3028858],
)
C(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/browser-autofill/browser_canonize.js; "
    "browser/components/urlbar/tests/browser/browser_canonizeURL.js; "
    "browser/components/urlbar/tests/browser-tabs/browser_notFoundPage.js; "
    "browser/base/content/test/siteIdentity/browser_navigation_failures.js",
    "Ctrl+Enter canonizing/completing a URL (and the pref that disables it), and the "
    "server-not-found error page including its Try Again button and private-window variant.",
    [3028887, 3029196, 3029060, 3029061, 3029186, 3029187, 3029188, 3029192, 3029194],
)
C(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/browser-results/browser_calculator.js; browser_unitConversion.js; "
    "browser_bestMatch.js; browser_dynamicResults.js; browser_suggestedIndex.js; browser_result_menu.js; "
    "browser_result_menu_general.js; browser_remove_match.js; browser_secondaryActions.js; "
    "browser_retainedResultsOnFocus.js; browser_autoselect.js; browser_heuristicNotAddedFirst.js; "
    "browser_result_onSelection.js; browser_results_format_displayValue.js; browser_tag_star_visibility.js; "
    "browser_testUrlbarIcons.js; browser_same_ref_deduplication.js",
    "Result-list mechanics: the calculator, unit conversion (including copying the result), best "
    "match, the per-result '...' menu and dismissal, removing a history/suggestion row, retained "
    "results and focus state, secondary actions, and the bookmark-star/tag row indicators.",
    [3073429, 3073430, 3073431, 3197474, 3197478, 3197495, 3028703, 3028704, 3028866,
     3028901, 3028903, 3029396, 3028864],
)
C(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/browser-search/browser_recentsearches.js; "
    "browser/components/urlbar/tests/browser-search/browser_searchHistoryLimit.js; "
    "browser/components/urlbar/tests/browser-results/browser_result_menu.js; "
    "browser/components/urlbar/tests/browser-search/browser_search_continuation.js",
    "Recent searches: enabling/disabling from about:config and about:preferences#search, the "
    "max-results prefs, zero-prefix display, suppression in search mode, removal via the result "
    "menu, the PBM isolation rules, persistence across update, and coexistence with trending "
    "predictions.",
    [3029353, 3029354, 3029355, 3029356, 3029357, 3029358, 3029359, 3029360, 3029361,
     3029362, 3029363, 3029367, 3029368, 3029369, 3029370, 3029376, 3029375],
)
C(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/browser-editing/browser_clipboard.js; "
    "browser/components/urlbar/tests/browser-editing/browser_paste_then_focus.js; "
    "browser/components/urlbar/tests/browser-results/browser_result_menu.js",
    "The clipboard suggestion row: the feature pref, the display limit, only-latest-link, "
    "links-only filtering, long links, multiple clipboard sources, dismissal from the result menu, "
    "dismissal on tab change, editing the inserted link and the www. prefix.",
    [3029320, 3029325, 3029326, 3029327, 3029328, 3029329, 3029330, 3029331, 3029332,
     3029333, 3029334],
)
C(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/quicksuggest/browser/browser_quicksuggest.js; "
    "browser_quicksuggest_addons.js; browser_quicksuggest_block.js; browser_quicksuggest_configuration.js; "
    "browser_quicksuggest_contextual_optin.js; browser_quicksuggest_dynamicSuggestions.js; "
    "browser_quicksuggest_indexes.js; browser_quicksuggest_mdn.js; browser_quicksuggest_yelp.js; "
    "browser_weather.js; browser_telemetry_suggestMetrics.js; browser_pickedSearchSuggestion.js",
    "Firefox Suggest: the preferences UI and every combination of the sponsored / non-sponsored / "
    "improve-the-experience switches, sponsored and non-sponsored results being triggered, the "
    "region-vs-locale gating, add-on suggestions and their dismissal, keyword-minimum-length, and "
    "the suggest telemetry.",
    [3029147, 3029148, 3029149, 3029150, 3029151, 3029152, 3029153, 3029154, 3029155,
     3029156, 3029157, 3029158, 3029278, 3029279, 3029281, 3029282, 3029285, 3029286,
     3029292, 3029336, 3029295, 3029297, 3029300, 3029294, 3197602],
)
C(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/browser-UrlbarInput/browser_searchTerms.js; browser_searchTerms_autofill.js; "
    "browser_searchTerms_backgroundTabs.js; browser_searchTerms_modifiedUrl.js; browser_searchTerms_moveTab.js; "
    "browser_searchTerms_popup.js; browser_searchTerms_revert.js; browser_searchTerms_revert_keyboard.js; "
    "browser_searchTerms_searchBar.js; browser_searchTerms_searchMode.js; browser_searchTerms_searchModeSwitcher.js; "
    "browser_searchTerms_strings.js; browser_searchTerms_stringsUnsafe.js; browser_searchTerms_switch_tab.js; "
    "browser_searchTerms_telemetry.js; browser_searchTerms_uri_mismatch.js; browser_searchTerms_remote_settings_sync.js",
    "Persist search term: the basic behaviour, interaction with search mode (same and different "
    "engine), follow-on searches, engine switching, keyboard access, session restore, the "
    "not-applicable cases (OpenSearch engines, secondary SERP tabs) and the search tip about it - "
    "17 dedicated in-tree tests.",
    [3029211, 3029213, 3029214, 3029222, 3029223, 3029232, 3029251, 3029252, 3029258,
     3029260, 3029261, 3029266, 3029296, 3029430, 3029431, 3029432, 3029433, 3029434,
     3029435, 3029436, 3029437, 3029438, 3029440, 3029441, 3029442, 3029443,
     3028954, 3028811, 3029254, 3029255, 3029256],
)
C(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/browser-search/browser_add_search_engine.js; "
    "browser_shortcuts_add_search_engine.js; browser_contextualsearch_install.js; browser_searchSettings.js; "
    "browser_action_searchengine.js; browser_action_searchengine_alias.js; browser_keyword.js; "
    "browser_keyword_override.js; browser_keywordSearch.js; browser_keywordSearch_postData.js; "
    "browser_separatePrivateDefault.js; browser_separatePrivateDefault_differentEngine.js; "
    "browser/components/preferences/tests/search/browser_search_engineList.js; browser_search_engine_reorder.js; "
    "browser_searchRestoreDefaults.js; browser_search_userEngineDialog.js; browser_searchDefaultEngine.js",
    "Adding an OpenSearch engine (from the page, the context menu, the Unified Search Button and "
    "about:preferences#search), making it default, assigning and using keywords/aliases, "
    "reordering and removing engines, restoring defaults, and the separate private-window default.",
    [3028768, 3028769, 3028779, 3028780, 3028782, 3028784, 3028794, 3028795, 3028796,
     3028807, 3028808, 3028809, 3029002, 3029003, 3029180, 3029181, 3029182, 3029341,
     3029342, 3029343, 3029344, 3029345, 3029346, 3197449, 3197451, 3197455, 3197458,
     3028828, 3028825, 3028826, 3028827, 3029382],
)
C(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/browser-search/browser_contextualsearch.js; browser_tabToSearch.js; "
    "browser_oneOffs.js; browser_oneOffs_contextMenu.js; browser_oneOffs_keyModifiers.js; "
    "browser_oneOffs_searchSuggestions.js; browser_oneOffs_settings.js; browser_oneOffs_heuristicRestyle.js; "
    "browser_groupLabels.js; browser_downArrowKeySearch.js; "
    "browser/components/urlbar/tests/browser-results/browser_secondaryActions.js",
    "Contextual search / tab-to-search with Amazon, DuckDuckGo, Bing, eBay, Wikipedia and Google, "
    "the install prompt when the engine is not present, secondary-action buttons, the one-off "
    "engine row and its context menu, and 'Search in New Tab'.",
    [3029397, 3029398, 3029399, 3029400, 3029401, 3029402, 3029406, 3029407, 3028801,
     3028800, 3029408, 3029409, 3029410, 3029411, 3029412, 3028869, 3028890],
)
C(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/browser/browser_top_sites.js; browser_top_sites_private.js; "
    "browser/components/urlbar/tests/browser-results/browser_top_sites_switchtab.js; "
    "browser/extensions/newtab/test/browser/ (27 tests); "
    "browser/components/urlbar/tests/browser-editing/browser_urlbar_contextmenu.js",
    "Top Sites / Shortcuts in the urlbar dropdown and on the new tab page: the tile context menu "
    "(pin, edit, dismiss, delete from history, open in new window / private window), creating a "
    "shortcut from an empty tile, sponsored-tile behaviour and its restrictions, position "
    "persistence, disabling top sites in the urlbar and on the homepage, and the link context "
    "menu on a tile.",
    [3029100, 3029101, 3029102, 3029103, 3029104, 3029105, 3029106, 3029107, 3029108,
     3029109, 3029110, 3029111, 3029112, 3029113, 3029114, 3029116, 3029117, 3029118,
     3029119, 3029120, 3029121, 3029122, 3029123, 3029125, 3029127, 3029128, 3029129,
     3029133, 3029137, 3029138, 3029140, 3029141, 3029142, 3029143, 3029145,
     3028791, 3028793, 3029646],
)
C(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/browser-tips/browser_searchTips.js; browser_searchTips_interaction.js; "
    "browser_interventions.js; browser_updateRefresh.js; browser_updateAsk.js; browser_updateRestart.js; "
    "browser_updateWeb.js; browser_picks.js; browser_selection.js; browser_tip_richSuggestion.js; "
    "browser_suppressTips.js",
    "Search tips and intervention cards: the refresh-Firefox intervention and its dialog, the "
    "restart-to-update button, the onboarding tip after an update, tip suppression and the "
    "per-tip display limit.",
    [3028756, 3028757, 3028761, 3028764, 3028765, 3028736, 3029243, 3029301],
)
C(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/browser/searchbar/ (16 tests); "
    "browser/components/urlbar/tests/browser-search/browser_searchSuggestions.js; browser_searchSettings.js; "
    "browser_placeholder.js; browser_selectStaleResults.js; browser_stopSearchOnSelection.js; "
    "browser/components/preferences/tests/search/browser_searchsuggestions.js; browser_searchShowSuggestionsFirst.js; "
    "browser_trendingsuggestions.js",
    "The legacy search bar: performing a search, results in a new tab, its options menu and "
    "keyboard shortcuts, disabling suggestions, the engine dropdown, the default-engine change, "
    "and Bookmarks/Tabs/History not appearing in it.",
    [3028767, 3028772, 3028773, 3028774, 3028775, 3028777, 3028778, 3028810, 3028735,
     3028804, 3028814, 3028819, 3029029, 3028915],
)
C(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/browser-tabs/browser_tabMatchesInAwesomebar.js; "
    "browser_tabMatchesInAwesomebar_perwindowpb.js; browser_switchToTab_chiclet.js; browser_switchToTab_closed_tab.js; "
    "browser_switchToTab_closes_newtab.js; browser_switchToTab_fullUrl_repeatedKeydown.js; browser_currentTab.js; "
    "browser_keepStateAcrossTabSwitches.js; browser_valueOnTabSwitch.js; browser_new_tab_urlbar_reset.js; "
    "browser_move_tab_to_new_window.js; browser_closesUrlbarPopup.js; browser_raceWithTabs.js; "
    "browser_paste_then_switch_tab.js; browser_action_tabgroups.js",
    "Switch-to-tab: the chiclet, matching open tabs, Ctrl-click behaviour, closed/new tab handling, "
    "urlbar state kept across tab switches, and the reset on a new tab.",
    [3028891, 3028862, 3028872, 3028914, 3028949, 3028962],
)
C(
    65334,
    "STRONG",
    "browser/components/places/tests/browser/; browser/components/places/tests/browser/interactions/; "
    "toolkit/components/places/tests/browser/; "
    "browser/components/urlbar/tests/browser-autofill/browser_inputHistory.js",
    "Frecency recalculation: on idle, on snippet run, the days-cutoff pref, recalculation for old "
    "history, and the increase/decrease on visit, bookmark, history removal, bookmark removal and "
    "bookmark URL edit.",
    [3029269, 3029270, 3029271, 3029272, 3029273, 3029274, 3029275, 3029276, 3029277],
)
C(
    65334,
    "STRONG",
    "browser/components/search/test/browser/telemetry/browser_search_telemetry_domain_categorization_reporting.js; "
    "browser_search_telemetry_domain_categorization_extraction.js; browser_search_telemetry_categorization_timing.js; "
    "browser_search_telemetry_domain_categorization_ping_submission.js; "
    "browser_search_telemetry_domain_categorization_reporting_timer.js; "
    "browser_search_telemetry_domain_categorization_reporting_timer_wakeup.js; "
    "browser_search_telemetry_domain_categorization_region.js; "
    "browser_search_glean_serp_event_telemetry_categorization_enabled_by_pref.js",
    "SERP categorization: on tab close, on navigating away, on idle and after the computer wakes.",
    [3029348, 3029349, 3029350, 3029351],
)
C(
    65334,
    "STRONG",
    "browser/components/search/test/browser/telemetry/browser_search_telemetry_spa_single_tab.js; "
    "browser_search_telemetry_spa_multi_tab.js; browser_search_telemetry_spa_multi_provider.js; "
    "browser_search_telemetry_spa_in_content.js; browser_search_telemetry_engagement_multiple_tabs.js; "
    "browser_search_telemetry_engagement_redirect.js; browser_search_telemetry_sources_navigation.js; "
    "browser/components/urlbar/tests/browser-search/browser_searchFunction.js",
    "Searching from a remote page / SERP for Google, Bing and DuckDuckGo, background searches, "
    "sub-search pages showing the full URL, and returning to a context-menu SERP.",
    [3029212, 3029231, 3029234, 3029238, 3029250, 3028909],
)
C(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/browser-search/browser_searchSingleWordNotification.js; "
    "browser/components/urlbar/tests/browser-search/browser_keywordSearch.js; browser_keyword_override.js",
    "The 'Did you mean to go to...' single-word infobar, the domain allow-list pref, and the "
    "alternate-fixup / dnsResolveSingle pref combinations.",
    [3029197, 3029199, 3029200, 3029201, 3029202, 3029203, 3029210, 3028898, 3028900],
)
# =============================================================== section 617196 (33)
CSEC(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/browser-results/; browser-autofill/browser_typed.js; browser_trimURLs.js; "
    "browser-searchMode/browser_searchModeSwitcher_basic.js; browser-tabs/browser_switchToTab_chiclet.js; "
    "browser-search/browser_searchSuggestions.js; browser_separatePrivateDefault.js; "
    "browser/components/urlbar/tests/browser-UrlbarInput/browser_trimURLs.js; "
    "browser/base/content/test/siteIdentity/browser_check_identity_state.js",
    "PREF MATRIX: this section is 'set pref X to its non-default value, confirm the corresponding "
    "urlbar behaviour changes' repeated for every browser.urlbar.* / browser.search.suggest.* / "
    "security.insecure_connection_text.* pref. Each of these prefs is exercised by the in-tree "
    "test for the feature it gates (suggestions, autofill, trimURLs, trimHttps, shortcuts.*, "
    "suggest.*, switchTabs.adoptIntoActiveWindow, showSearchSuggestionsFirst, insecure-connection "
    "text).",
    [617196],
)
# =============================================================== section 617192 (82)
C(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/browser-editing/browser_ime_composition.js; browser_pasteAndGo.js; "
    "browser_urlbar_contextmenu.js; browser_selectionKeyNavigation.js; browser_decode.js; browser_percent_encoded.js; "
    "browser/components/urlbar/tests/browser-search/browser_keyword.js; browser_oneOffs.js; browser_oneOffs_settings.js; "
    "browser_oneOffs_contextMenu.js; browser_searchSuggestions.js; browser_searchHistoryLimit.js; "
    "browser/components/urlbar/tests/browser-results/browser_remove_match.js; browser_result_menu.js; "
    "browser/components/urlbar/tests/browser-searchMode/browser_alias_replacement.js; browser_engineRemoval.js; "
    "browser/components/urlbar/tests/browser-tabs/browser_tabMatchesInAwesomebar.js; browser_currentTab.js; "
    "browser/components/urlbar/tests/browser-autofill/browser_typed.js; browser_firstResult.js; "
    "browser/components/urlbar/tests/browser-UrlbarInput/browser_a11y.js; browser_overflow.js",
    "The regression-bug backlog in this section maps onto the same mechanics the tree covers: IME "
    "typing, Ctrl+K / Ctrl+E behaviour, keyword and alias offers, removing suggestions and history "
    "rows from the dropdown, one-off engine settings, switch-to-tab labelling, autofill of "
    "unvisited bookmarks, percent/ASCII unescaping, data-URI handling, selection manipulation, "
    "Paste and Go, drag-and-drop in the bar, and dropdown focus behaviour.",
    [3028713, 3028762, 3028846, 3028852, 3028857, 3028860, 3028863, 3028878, 3028882, 
     3028885, 3028902, 3028908, 3028913, 3029388, 3028731, 3028710, 3028845, 3028867, 
     3028874, 3117649],
)
# =============================================================== section 617194 (19)
C(
    65334,
    "STRONG",
    "browser/components/urlbar/tests/browser-results/browser_tag_star_visibility.js; browser_testUrlbarIcons.js; "
    "browser_blobIcons.js; "
    "browser/base/content/test/siteIdentity/browser_check_identity_state.js; browser_geolocation_indicator.js; "
    "browser_tab_sharing_state.js; "
    "browser/base/content/test/permissions/browser_permissions.js; browser_temporary_permissions.js; "
    "browser/base/content/test/webrtc/browser_devices_get_user_media.js; "
    "browser/base/content/test/protectionsUI/browser_protectionsUI_icon_state.js; browser_protectionsUI_shield_visibility.js; "
    "browser/base/content/test/zoom/browser_default_zoom.js; browser_default_zoom_sitespecific.js",
    "The identity-block indicator set: bookmark star, permission-granted, secure/insecure "
    "connection, tracking protection shield, notification, geolocation, camera+microphone, "
    "persistent storage and screen sharing - plus the zoom indicator.",
    [3028935, 3028936, 3028946, 3028947, 3028952, 3028953, 3029018, 3029019, 3029020,
     3029021, 3029022, 3029023, 3029024, 3029025, 3029026, 3029027, 3029340],
)
# =============================================================== section 617195 (6)
C(
    65334,
    "STRONG",
    "browser/components/enterprisepolicies/tests/browser/browser_policy_search_engine.js; "
    "browser/components/preferences/tests/search/browser_search_engineList_enterprise.js",
    "The SearchEngines enterprise policy setting the default engine, adding and removing engines, "
    "and flipping the corresponding pref.",
    [3029179, 3029204, 4077175],
)
# =============================================================== MEDIUM
C(
    65334,
    "MEDIUM",
    "browser/components/urlbar/tests/browser-UrlbarInput/browser_a11y.js; "
    "browser/components/urlbar/tests/browser-results/browser_result_a11y_label.js; "
    "browser/components/urlbar/tests/browser-UrlbarView/",
    "Everything visual and environmental in this suite: theme variants (Alpenglow / Dark / Light / "
    "Proton), High Contrast, RTL builds, low resolution and window-resize layout, HiDPI, screen "
    "readers, the macOS touch bar, touch input, and the live-language-switch matrix (which "
    "re-checks every localised surface after switching locale at runtime). Also the real-partner "
    "default-search-code checks, GPO/plist policy delivery, and the Semantic Search / Google Lens "
    "feature gates.",
    [3028797, 3028877, 3028920, 3028921, 3028922, 3028923, 3028927, 3028929, 3028957,
     3028958, 3028963, 3028964, 3028965, 3028966, 3028968, 3028969, 3028970, 3028972,
     3028973, 3028974, 3028975, 3028976, 3028978, 3028979, 3028980, 3028981, 3028983,
     3028984, 3028985, 3028987, 3028988, 3028989, 3028990, 3028991, 3028993, 3028994,
     3028995, 3028996, 3028997, 3028999, 3029000, 3029001, 3028933, 3028934,
     3028865, 3028868, 3028871, 3028873, 3028875, 3028876, 3028879, 3028894, 3028895,
     3028896, 3028904, 3028907, 3028910, 3028912, 3028853, 3028855, 3028856, 3028859,
     3029298, 3029299, 3029322, 3029323, 3029324,
     3029159, 3029160, 3029161, 3029162, 3029163, 3029164, 3029165, 3029166, 3029167,
     3029168, 3029169, 3029170, 3029171, 3029172, 3029173, 3029174, 3029175, 3029176,
     3029177, 3029178,
     3029189, 3029190, 3029191, 3029193, 3029195,
     3029283, 3029284, 3029287, 3029280,
     3029371, 3029372, 3029373, 3029374,
     3029390, 3029391, 3029403, 3029404, 3029405, 3029413, 3029414, 3029415,
     3029424, 3029425, 3029428, 3029429, 3029096, 3029097,
     3029765, 3029766, 3029767, 3029768, 3029769, 3029770,
     3029183, 3029184, 3029185,
     3029337, 3197503, 3197564, 3029131, 3029132, 3029134, 3029136, 3029139, 3029144,
     3028918, 3028919, 3028950, 3028951, 3028955, 3028956, 3028961, 3029005, 3029006,
     3029007, 3029009, 3029010, 3029011, 3029012, 3029013, 3029014, 3029015, 3029016,
     3029028, 3029037, 3029065, 3029066, 3029067, 3029068, 3029069, 3029229, 3029249,
     3029259, 3029263, 3029302, 3029303, 3029304, 3029305, 3029306, 3029307, 3029308,
     3029309, 3029310, 3029311, 3029312, 3029313, 3029314, 3029315, 3029316, 3029317,
     3029318, 3029319, 3144876, 3144877, 3903514, 4031553,
     3028717, 3028720, 3028721, 3028728, 3028829, 3028830, 3028831, 3028832, 3028833,
     3028834, 3028835, 3028836, 3028705],
)
# The "[to remove]" / "[review/remove]" section - retire rather than de-prioritise.
CSEC(
    65334,
    "MEDIUM",
    "n/a - these cases are already marked for removal in their own titles",
    "Section 665881 is explicitly tagged '[to remove]', '[review/remove]', '[duplicate]' or "
    "'[TO BE REMOVED]' by the manual team. Retire them rather than re-triaging.",
    [665881],
)
