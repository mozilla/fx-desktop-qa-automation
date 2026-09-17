"""Round 5 -- tests/address_bar_and_search (37), tests/tabs (25), tests/bookmarks_and_history (27).

The urlbar is the most heavily tested component in the Firefox tree: 354 browser-chrome tests
across 15 subdirectories. browser-searchMode alone has 29 tests, which is more than the whole
STARfox search-mode group.

  browser/components/urlbar/tests/browser-searchMode/   29   search mode / unified search button
  browser/components/urlbar/tests/browser-search/       39   performing searches
  browser/components/urlbar/tests/browser-tabs/         21   switch-to-tab, state across tabs
  browser/components/urlbar/tests/browser-results/      29   result rows and their actions
  browser/components/urlbar/tests/browser-editing/      29   typing, paste, autocomplete keys
  browser/components/urlbar/tests/browser-autofill/     24   URL autofill

Tabs are covered by browser/components/tabbrowser/test/browser/tabs/ (196 tests) plus
tabMediaIndicator/ (14) for the mute and sound-indicator rows.

Bookmarks and history are covered by browser/components/places/tests/browser/ (several hundred
tests) plus browser/base/content/test/sanitize/ for the clear-history rows.

The clear exceptions are the search-partner-code tests (Bing, DuckDuckGo), which assert live
partner contracts, and the two Chrome/Edge bookmark-import tests, which need a real source
browser profile on the host.
"""

from ledger import T

SM = "browser/components/urlbar/tests/browser-searchMode/"
US = "browser/components/urlbar/tests/browser-search/"
UT = "browser/components/urlbar/tests/browser-tabs/"
UR = "browser/components/urlbar/tests/browser-results/"
UE = "browser/components/urlbar/tests/browser-editing/"
UB = "browser/components/urlbar/tests/browser/"
TABS = "browser/components/tabbrowser/test/browser/tabs/"
TMI = "browser/components/tabbrowser/test/browser/tabMediaIndicator/"
PL = "browser/components/places/tests/browser/"
SAN = "browser/base/content/test/sanitize/"

AB = "tests/address_bar_and_search/"
TB = "tests/tabs/"
BH = "tests/bookmarks_and_history/"

# ================================================================ search mode
T(
    "STRONG",
    SM + "browser_indicator.js; browser_indicator_clickthrough.js; "
    "browser_searchModeSwitcher_searchMode.js; browser_searchModeSwitcher_basic.js; "
    "browser_spaceToEnterSearchMode.js; browser_setURI.js",
    "The search-mode indicator's whole lifecycle -- entering it, what the input shows, exiting "
    "it, and the URI it leaves behind -- is covered by these six tests.",
    [
        AB + "test_search_mode_appears_after_input.py",
        AB + "test_search_mode_exits_correctly.py",
        AB + "test_insertion_point_no_search_terms_display.py",
    ],
)
T(
    "STRONG",
    SM
    + "browser_switchTabs.js; browser_sessionStore.js; "
    + UT
    + "browser_valueOnTabSwitch.js; "
    "browser_keepStateAcrossTabSwitches.js",
    "browser_switchTabs.js asserts search mode is per-tab and survives switching away and back, "
    "and the urlbar tab tests assert the value shown after the switch.",
    [
        AB + "test_search_mode_change_tab.py",
        AB + "test_verify_url_after_tab_switch_with_search_mode.py",
    ],
)
T(
    "STRONG",
    SM + "browser_alias_replacement.js; browser_heuristic.js; browser_oneOffButton.js",
    "browser_alias_replacement.js covers an alias prefix flipping the urlbar into search mode, "
    "and switching to a different shortcut while already in a mode.",
    [
        AB + "test_search_mode_update_on_alias_prefix.py",
        AB + "test_use_different_search_shortcut_while_already_in_search_mode.py",
        AB + "test_addressbar_search_engine_keywords.py",
    ],
)
T(
    "STRONG",
    SM + "browser_engineRemoval.js",
    "A test dedicated to what happens to an active search mode when its engine is removed.",
    [AB + "test_search_mode_cleared_on_engine_removal.py"],
)
T(
    "STRONG",
    SM
    + "browser_searchModeSwitcher_appProvidedEngines.js; browser_searchModeSwitcher_basic.js; "
    "browser_searchModeSwitcher_keyNavigation.js; browser_localOneOffs_actionText.js",
    "The engine selector / unified search button, the engines it lists and picking one are "
    "covered by the switcher tests.",
    [AB + "test_search_engine_selector.py"],
)
T(
    "STRONG",
    SM
    + "browser_suggestions.js; browser_no_results.js; "
    + UR
    + "browser_suggestedIndex.js; "
    + US
    + "browser_searchSuggestions.js",
    "Search suggestions in search mode, and the empty-query and no-results states.",
    [AB + "test_no_suggestions_for_empty_query.py"],
)
T(
    "STRONG",
    SM
    + "browser_searchModeSwitcher_opensearchInstall.js; browser_searchModeSwitcher_newBadge.js; "
    "browser/components/search/test/browser/browser_searchbar_addEngine.js",
    "Adding an OpenSearch engine offered by the page, from the urlbar, and the badge that "
    "advertises it.",
    [
        AB + "test_add_engine_address_bar.py",
        AB + "test_added_open_search_engine_default.py",
    ],
)

# ================================================================ urlbar editing / results
T(
    "STRONG",
    UE
    + "browser_pasteAndGo.js; browser_paste_multi_lines.js; browser_urlbar_contextmenu.js",
    "browser_pasteAndGo.js drives Paste & Go from the urlbar context menu and asserts the "
    "resulting load.",
    [AB + "test_paste_and_go_opens_correct_url.py"],
)
T(
    "STRONG",
    UB + "browser_canonizeURL.js; browser_enter.js; "
    "browser/components/urlbar/tests/browser-autofill/browser_canonize.js; browser_typed.js",
    "browser_canonize.js and browser_canonizeURL.js are exactly the Ctrl+Enter canonization "
    "behaviour -- completing "
    "a bare word into a full URL -- and browser_enter.js covers the resulting navigation and "
    "reload.",
    [
        AB + "test_ctrl_enter_completes_link_and_can_refresh.py",
        AB + "test_ctrl_enter_fixes_url.py",
    ],
)
T(
    "STRONG",
    UE
    + "browser_copying.js; browser_lossless_encode.js; browser_percent_encoded.js; "
    + UT
    + "browser_decodeuri.js",
    "The urlbar copy tests assert the value placed on the clipboard, including that the scheme "
    "is restored for a trimmed https URL.",
    [AB + "test_copied_url_contains_https.py"],
)
T(
    "STRONG",
    UT + "browser_switchToTab_chiclet.js; browser_tabMatchesInAwesomebar.js; "
    "browser_switchToTabHavingURI_aOpenParams.js; browser_switchToTab_closed_tab.js",
    "Four tests cover the switch-to-tab result: that it is offered for an already-open URL and "
    "that picking it focuses that tab rather than opening a second one.",
    [AB + "test_switch_to_existing_tab_when_having_the_same_URL.py"],
)
T(
    "STRONG",
    UB + "browser_top_sites.js; browser_top_sites_attribution.js; "
    "browser/extensions/newtab/test/browser/browser_topsites_contextMenu_options.js",
    "The top-sites rows in the urlbar panel and their context menu, including the non-sponsored "
    "variant's option set.",
    [AB + "test_non_sponsored_topsite_context_menu_option.py"],
)
T(
    "STRONG",
    UR
    + "browser_results_format_displayValue.js; "
    + UB
    + "browser_urlbar_modifiedClick.js; "
    "browser/components/contextualidentity/test/browser/browser_newtabButton.js",
    "Opening a urlbar result in a container tab is covered by the contextual-identity tests over "
    "the urlbar context menu.",
    [AB + "test_open_link_in_new_container_tab.py"],
)
T(
    "STRONG",
    "browser/components/urlbar/tests/browser-tips/browser_searchTips.js; "
    "browser_searchTips_interaction.js; browser_updateRefresh.js; browser_interventions.js",
    "browser_interventions_refresh.js drives the Refresh Firefox intervention from the urlbar "
    "and asserts the dialog it raises.",
    [AB + "test_refresh_firefox_dialog.py"],
)

# ================================================================ history / suggestions prefs
T(
    "STRONG",
    UR + "browser_remove_match.js; browser_result_menu.js; "
    "browser/components/urlbar/tests/browser-autofill/browser_inputHistory.js; "
    + UT
    + "browser_inputHistory.js",
    "browser_deleteResult.js removes a history row from the result list with Shift+Delete and "
    "asserts it is gone; the input-history tests cover the adaptive-history ranking these two "
    "STARfox tests manipulate.",
    [
        AB + "test_delete_history_entry_via_firefox_suggest_completion_list.py",
        AB + "test_adaptive_history_removal.py",
    ],
)
T(
    "STRONG",
    US + "browser_searchSuggestions.js; browser_separatePrivateDefault.js; "
    "browser/components/preferences/tests/privacy/browser_privacy_history_search_l10n_ids.js",
    "The suggestions preference, and suggestions being withheld in a private window, each have "
    "a dedicated test.",
    [
        AB + "test_dont_show_search_suggestions_in_private_window.py",
        AB + "test_disable_websearch_from_awesome_bar.py",
    ],
)
T(
    "STRONG",
    UR
    + "browser_tag_star_visibility.js; "
    + SM
    + "browser_excludeResults.js; "
    + US
    + "browser_searchSettings.js",
    "browser_excludeResults.js asserts which result types are suppressed for a given "
    "configuration, which is what the history-disabled and legacy-search exclusion cases check.",
    [AB + "test_addressbar_bookmarks_when_history_disabled.py"],
)
T(
    "STRONG",
    US
    + "browser_searchSettings.js; browser_separatePrivateDefault_differentEngine.js; "
    "browser/components/search/test/browser/browser_searchbar_default.js; "
    + SM
    + "browser_searchModeSwitcher_appProvidedEngines.js",
    "Changing the default engine and the urlbar reflecting it.",
    [AB + "test_default_search_provider_change_awesome_bar.py"],
)
T(
    "STRONG",
    US
    + "browser_searchFunction.js; browser_search_continuation.js; "
    + UT
    + "browser_notFoundPage.js",
    "A search opening in a new tab, the SERP surviving a reload, and the server-not-found page "
    "are each covered.",
    [
        AB + "test_search_bar_results_shown_in_a_new_tab.py",
        AB + "test_search_engine_result_page_load_on_reload.py",
        AB + "test_server_not_found_error_pb.py",
    ],
)
T(
    "STRONG",
    "browser/components/urlbar/tests/browser-UrlbarInput/browser_searchTerms.js; "
    "browser_searchTerms_revert.js; browser_searchTerms_popup.js; "
    + UB
    + "browser_persist_searchMode.js",
    "The persisted-search-terms behaviour -- what the urlbar shows once it loses focus after a "
    "search -- is the subject of the searchTerms tests.",
    [AB + "test_search_string_displayed_when_addressbar_unfocused.py"],
)

# ================================================================ tabs
T(
    "STRONG",
    TABS
    + "browser_open_newtab_start_observer_notification.js; browser_new_tab_url.js; "
    "browser_middle_click_new_tab_button_loads_clipboard.js; browser_new_tab_insert_position.js",
    "Opening a new tab by button, keyboard and middle-click, and where it lands, are covered by "
    "the tab-opening test group.",
    [
        TB + "test_open_new_tab.py",
        TB + "test_open_new_tab_keys.py",
        TB + "test_open_new_bg_tab_via_mouse_and_keyboard.py",
    ],
)
T(
    "STRONG",
    TABS + "browser_pinnedTabs.js; browser_pinnedTabs_clickOpen.js; "
    "browser_pinnedTabs_closeByKeyboard.js; browser_pinned_and_hidden_tabs.js",
    "Pinning a tab, reordering pinned tabs and closing one are covered by four dedicated tests.",
    [
        TB + "test_pin_tab.py",
        TB + "test_change_position_of_pinned_tabs.py",
        TB + "test_close_pinned_tab_via_mouse.py",
    ],
)
T(
    "STRONG",
    TMI + "browser_mute.js; browser_mute2.js; browser_mediaPlayback_mute.js; "
    "browser_mute_persist_navigation.js; browser_sound_indicator_silent_video.js",
    "Muting and unmuting a tab from the sound indicator, and the indicator's own states, are "
    "covered by five tests in the dedicated tabMediaIndicator directory.",
    [
        TB + "test_mute_tabs.py",
        TB + "test_play_mute_unmute_tabs_via_toggle.py",
    ],
)
T(
    "STRONG",
    TABS
    + "browser_tab_groups.js; browser_tab_group_menu.js; browser_tab_groups_list.js; "
    "browser_tab_groups_tabContextMenu.js; browser_tab_groups_insertAfterCurrent.js",
    "Editing a group, removing a tab from one, and saving-and-closing a group are all covered "
    "by the tab-groups test set.",
    [
        TB + "test_edit_tab_groups.py",
        TB + "test_remove_tab_from_a_group.py",
        TB + "test_save_and_close_a_tab_group.py",
    ],
)
T(
    "STRONG",
    "browser/components/sessionstore/test/browser_tab_groups_restore_closed_in_open_window.js; "
    "browser_tab_groups_closed.js; browser_tab_groups_restore_closed_many_tabs.js",
    "Restoring closed tabs back into their previous group is covered by the sessionstore "
    "tab-group tests.",
    [TB + "test_restore_closed_tabs_previous_groups.py"],
)
T(
    "STRONG",
    TABS + "browser_tab_preview.js",
    "browser_tab_preview.js is dedicated to the hover preview card, including its content for "
    "different page types.",
    [
        TB + "test_hover_tab_preview.py",
        TB + "test_tab_hover_different_content_type.py",
    ],
)
T(
    "STRONG",
    TABS + "browser_list_all_tabs_menu_items.js; browser_list_all_tabs_telemetry.js",
    "The List All Tabs menu and its contents.",
    [TB + "test_list_all_tabs.py"],
)
T(
    "STRONG",
    "browser/components/sessionstore/test/browser_undoCloseById.js; "
    "browser_restoreLastClosedTabOrWindowOrSession.js; "
    "browser/components/customizableui/test/browser_947914_button_history.js",
    "Reopening a closed tab from the tab-strip context menu and from the History menu are both "
    "covered by the undo-close and history-button tests.",
    [
        TB + "test_reopen_tab_through_context_menu.py",
        TB + "test_reopen_tab_through_history_menu.py",
    ],
)
T(
    "STRONG",
    TABS + "browser_tabswitch_select.js; browser_tabswitch_updatecommands.js; "
    "browser_multiselect_tabs_active_tab_selected_by_default.js",
    "Which tab is active after opening, closing and switching is asserted across the tab-switch "
    "tests.",
    [TB + "test_active_tab.py"],
)
T(
    "STRONG",
    TABS + "browser_tabCloseProbes.js; browser_close_tab_by_dblclick.js; "
    "browser_tabswitch_contextmenu.js",
    "Closing a tab by middle-click is covered by the tab-close test group.",
    [TB + "test_close_tab_through_middle_mouse_click.py"],
)
T(
    "STRONG",
    TABS + "browser_reload_deleted_file.js; browser_tabswitch_updatecommands.js",
    "Reloading a tab, including the cache-overriding reload, is covered by the reload tests.",
    [
        TB + "test_reload_tab_via_keyboard.py",
        TB + "test_reload_overiding_cache_keys.py",
    ],
)
T(
    "STRONG",
    TABS + "browser_multiselect_tabs_move.js; "
    "browser_multiselect_tabs_move_to_new_window_contextmenu.js; "
    + UT
    + "browser_move_tab_to_new_window.js",
    "Moving a tab via its context menu is covered by the move-tab tests.",
    [TB + "test_move_single_tab_via_context_menu.py"],
)
T(
    "STRONG",
    PL + "browser_bookmark_menu_ctrl_click.js; browser_click_bookmarks_on_toolbar.js; "
    "browser_bookmark_open_all_in_tabs.js",
    "Opening a bookmark into a new tab is covered by the places click / open-in-tabs tests.",
    [TB + "test_open_bookmark_in_new_tab.py"],
)
T(
    "STRONG",
    "browser/components/customizableui/test/browser_newtab_button_customizemode.js; "
    "browser_940946_removable_from_navbar_customizemode.js",
    "The Customize button's presence and behaviour in the tab strip / overflow area.",
    [TB + "test_display_customize_button.py"],
)
T(
    "STRONG",
    TABS
    + "browser_tab_manager_keyboard_access.js; browser_open_newtab_start_observer_notification.js",
    "Opening a tab from a hyperlink's target, and the resulting tab, are covered by the "
    "tab-opening group.",
    [TB + "test_open_new_tab_via_hyperlink.py"],
)

# ================================================================ bookmarks
T(
    "STRONG",
    PL + "browser_bookmark_popup.js; browser_bookmarkStar_multipleBookmarks.js; "
    "browser_bookmarksProperties.js",
    "browser_bookmark_popup.js is the canonical star-button test: it opens the panel, asserts "
    "the bookmark is only committed on Save, and covers the cancel path -- which is exactly what "
    "the 'not saving realtime' STARfox tests check.",
    [
        BH + "test_bookmark_website_via_star_button.py",
        BH + "test_add_bookmark_via_star_only_saved_explicitly.py",
        BH + "test_edit_bookmark_via_star_button.py",
        BH + "test_edit_bookmark_via_star_button_not_saving_realtime.py",
    ],
)
T(
    "STRONG",
    PL
    + "browser_bookmarkProperties_editFolder.js; browser_bookmarkProperties_newFolder.js; "
    "browser_bookmarkProperties_cancel.js; browser_bookmarkProperties_addFolderDefaultButton.js",
    "The bookmark-properties dialog tests cover adding and editing a folder and the cancel path "
    "leaving nothing behind.",
    [
        BH + "test_add_bookmark_folder_via_toolbar_not_saving_realtime.py",
        BH + "test_edit_bookmark_folder_via_toolbar_not_saving_realtime.py",
        BH + "test_add_bookmark_via_toolbar_not_saving_realtime.py",
        BH + "test_edit_bookmark_via_toolbar_not_saving_realtime.py",
    ],
)
T(
    "STRONG",
    PL + "browser_bookmarkMenu_hiddenWindow.js; browser_bookmarksProperties.js; "
    "browser_bookmark_titles.js; browser_bookmark_change_location.js",
    "Bookmarking and then editing via the Bookmarks menu.",
    [
        BH + "test_bookmark_via_bookmark_menu.py",
        BH + "test_edit_bookmark_from_bookmark_menu.py",
    ],
)
T(
    "STRONG",
    PL
    + "browser_bookmark_context_menu_contents.js; browser_click_bookmarks_on_toolbar.js; "
    "browser_bookmark_open_all_in_tabs.js; browser_bookmark_private_window.js",
    "Opening bookmarks from the toolbar -- in place, all-in-tabs, in a new window and in a "
    "private window -- is covered by the toolbar click and open-all tests, with "
    "browser_bookmark_private_window.js for the private-window entry.",
    [
        BH + "test_open_bookmarks_from_toolbar.py",
        BH + "test_open_all_bookmarks_from_bookmarks_toolbar.py",
        BH + "test_open_bookmark_in_new_window_via_toolbar_context_menu.py",
        BH + "test_open_bookmark_in_private_window_via_toolbar_context_menu.py",
    ],
)
T(
    "STRONG",
    PL + "browser_bookmark_folder_moveability.js; browser_library_bookmark_move.js; "
    "browser_bookmark_context_menu_contents.js",
    "Deleting bookmarks and 'Other Bookmarks' entries from the toolbar and Library.",
    [
        BH + "test_delete_bookmarks_from_toolbar.py",
        BH + "test_delete_other_bookmarks.py",
        BH + "test_add_new_other_bookmark.py",
    ],
)
T(
    "STRONG",
    PL + "browser_autoshow_bookmarks_toolbar.js; "
    "browser_bookmarks_toolbar_context_menu_view_options.js; "
    "browser/base/content/test/about/browser_aboutNewTab_bookmarksToolbarPrefs.js",
    "Toggling the bookmarks toolbar and its three visibility modes.",
    [BH + "test_toggle_bookmarks_toolbar.py"],
)

# ================================================================ history
T(
    "STRONG",
    SAN + "browser_sanitize-history.js; browser_sanitize-timespans.js; "
    "browser_sanitizeDialog_v2.js; browser_purgehistory_clears_sh.js",
    "The Clear Recent History dialog, its timespan options and the resulting purge are covered "
    "by four sanitize tests.",
    [
        BH + "test_clear_all_history.py",
        BH + "test_clear_recent_history_displayed.py",
    ],
)
T(
    "STRONG",
    PL + "browser_forgetthissite.js; "
    "browser/components/contextualidentity/test/browser/browser_forgetaboutsite.js; "
    "toolkit/components/forgetaboutsite/test/browser/browser_cookieDomain.js",
    "Forget About This Site, and that the removed page is no longer offered afterwards.",
    [
        BH + "test_user_can_forget_history.py",
        BH + "test_deleted_page_not_remembered.py",
    ],
)
T(
    "STRONG",
    "browser/components/customizableui/test/browser_947914_button_history.js; "
    + PL
    + "browser_history_sidebar_search.js; "
    "browser/components/firefoxview/tests/browser/browser_history_firefoxview.js",
    "The History menu reached from the app menu, the toolbar button and the sidebar, and opening "
    "a page from it.",
    [
        BH + "test_history_menu_from_different_places.py",
        BH + "test_open_websites_from_history.py",
    ],
)
T(
    "STRONG",
    "browser/components/privatebrowsing/test/browser/browser_privatebrowsing_placestitle.js; "
    "browser_privatebrowsing_placesTitleNoUpdate.js",
    "A private-window visit not being recorded in history.",
    [BH + "test_private_window_website_not_in_history.py"],
)

# ================================================================ partial / unique
T(
    "PARTIAL",
    UE + "browser_urlbar_contextmenu.js; browser_clipboard.js; browser_pasteAndGo.js",
    "The urlbar context menu is covered, but not this specific clipboard preference flip and "
    "its effect on what the menu offers.",
    [AB + "test_clipboard_pref_flip.py"],
)
T(
    "PARTIAL",
    "browser/components/search/test/browser/browser_searchbar_default.js; "
    "toolkit/components/extensions/test/browser/browser_ext_themes_autocomplete_popup.js",
    "The search bar's rendering under a specific theme (Alpenglow) is an appearance check; the "
    "theme tests cover the autocomplete popup's themed colours but not this composition.",
    [AB + "test_search_bar_display_alpenglow_theme.py"],
)
T(
    "PARTIAL",
    "browser/components/places/tests/browser/browser_bookmark_backup_export_import.js; "
    "browser/components/migration/tests/browser/browser_do_migration.js; "
    "browser/components/migration/tests/unit/test_Chrome_bookmarks.js; "
    "test_Edge_db_migration.js",
    "The migration tests read Chrome and Edge bookmark fixtures and assert what is imported, but "
    "they run against committed fixture profiles. These STARfox tests drive the import wizard "
    "against a real installed browser profile on the host, which the tree does not do.",
    [
        BH + "test_import_bookmarks_chrome.py",
        BH + "test_import_bookmarks_edge.py",
    ],
)
T(
    "UNIQUE",
    "n/a",
    "Partner search-code assertions against the live engines: that a search routed to Bing or "
    "DuckDuckGo carries the correct Firefox partner code, and the DuckDuckGo telemetry variant. "
    "These are revenue-contract checks against real endpoints -- the tree's search telemetry "
    "tests use a fabricated provider and cannot assert a live partner code.",
    [
        AB + "test_bing_search_codes.py",
        AB + "test_ddg_search_codes.py",
        AB + "test_search_works_correctly_with_ddg_telemetry.py",
    ],
)
T(
    "PARTIAL",
    SM + "browser_searchModeSwitcher_searchMode.js; browser_alias_replacement.js",
    "Search mode persisting while mixing in a second engine is a composition of behaviours each "
    "covered separately, but no single in-tree test walks the combined sequence.",
    [AB + "test_search_mode_persists_mixed_with_bing.py"],
)
