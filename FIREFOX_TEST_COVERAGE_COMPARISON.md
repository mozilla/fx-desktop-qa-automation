# STARfox ↔ Firefox Desktop Test Coverage Comparison

**Generated:** 2026-07-14
**STARfox repo:** `fx-desktop-qa-automation` @ `main`
**Firefox tree:** `github.com/mozilla-firefox/firefox` @ `main` (mozilla-central mirror)

## Method & scope

- **STARfox side:** ~395 Selenium end-to-end UI smoke tests across 30 feature suites (`tests/*/test_*.py`).
- **Firefox side:** the `browser/` and `toolkit/` subtrees were pulled recursively and filtered to **browser-chrome (mochitest-browser) UI tests** — `**/test*/browser*/browser_*.js`. That yields **4,939 test files across 128 components**. Plain mochitest, xpcshell, web-platform-tests and marionette were excluded by design (they are unit/internal, with no E2E analog).
- **Matching level:** *feature / user-capability*, not identical assertions. STARfox is end-to-end UI automation; Firefox browser-chrome tests are integration-level. "Same feature" = same user-facing capability exercised.
- **Comparison run** by 7 parallel domain agents, each reading the STARfox tests locally and matching against the Firefox inventory. FF tests are only referenced where they actually appear in the tree.

## Headline numbers

| Domain | STARfox tests | FF browser-chrome (in-scope) | STARfox w/ FF counterpart | Direction of biggest gap |
|---|---|---|---|---|
| Address bar & search | 54 | ~330 | ~48 (89%) | Quick actions, urlbar keyboard/editing, result types |
| Tabs / session / toolbar | 39 | ~150 (of 440) | ~37 (95%) | Tab drag-drop, split view, session/window restore |
| Security / privacy / net / notif / geo | 86 | ~340 | ~74 UI-level | Anti-tracking *behavior*, storage access, WebRTC lifecycle |
| Password manager & form autofill | 68 | ~200 | ~60 (88%) | Address capture doorhanger, import, breach alerts, Megalist |
| Bookmarks / history / downloads / prefs / profiles | 61 | ~510 | ~40 (65%) | SelectableProfiles, Library window, Search prefs pane |
| PDF / print / reader / find / media / zoom | ~43 | ~200 | ~35% of areas | Picture-in-Picture (0 tests), print settings, per-site zoom |
| Sidebar / AI / menus / drag&drop / pocket / sync | ~44 | ~350 | ~30 (8–10%) | AI Window, sidebar tool panels, tab groups, Sync prefs |
| **Totals** | **~395** | **~2,370 mapped** | **~62% have a counterpart** | — |

**Two-sentence read:** STARfox's ~395 tests map cleanly onto Firefox's own UI tests about 62% of the time — the happy paths of each feature are well covered. In the reverse direction STARfox covers only a small slice (well under 15%) of Firefox's user-facing browser-chrome surface, and there are several *entire shipping features* with zero STARfox coverage.

## Cross-cutting findings (read these first)

1. **STARfox's differentiator is real-world/live-site E2E** — password autofill on Facebook/Google/Reddit/Taobao, real partner search-codes per region (Google/Bing/DDG/Ecosia/Qwant), real-server FxA sign-in, and download telemetry. Firefox browser-chrome uses synthetic pages and mock engines, so these have **no FF counterpart** and are worth protecting.
2. **`tests/drag_and_drop/` is misnamed** — it is *clipboard copy/paste* in web editors (Sheets/Zoho), **not** UI/tab drag-and-drop. Firefox's `browser_drag*` tests are tab-strip DnD. Real tab drag-and-drop has **zero** STARfox coverage.
3. **`tests/pocket/` is fully skipped** (`"Pocket tests no longer belong to DTE."`) and Firefox has essentially no Pocket browser-chrome tests either — effectively a dead area on both sides.
4. **Panel-text vs behavior gap in security** — STARfox verifies the ETP/trust panel *says* things are blocked, but never verifies a tracker's cookie/localStorage/cache is actually blocked or partitioned. Firefox's ~190 anti-tracking behavior tests have no STARfox analog.
5. **Several brand-new features are entirely untested in STARfox:** Picture-in-Picture (~85 FF tests), AI Window / Smart Window (~100), SelectableProfiles multi-profile UI (~20), Split View (~15), Link Preview / Page Assist.

---

# Part 1 — Test overlap (tests covering the same feature)

Below, each domain lists STARfox tests that have a clear Firefox browser-chrome counterpart. Grouped by sub-area. "STARfox-unique" = no meaningful FF browser-chrome equivalent.

## 1.1 Address bar & search (STARfox 54 → ~48 mapped)

| STARfox test | Feature | Matching Firefox test(s) |
|---|---|---|
| test_adaptive_history_autofill | Adaptive history autofill | browser-autofill/browser_originToAdaptive.js, browser_inputHistory_autofill.js |
| test_adaptive_history_removal | Remove adaptive-history entry | browser/browser_remove_match.js, browser_inputHistory.js |
| test_add_engine_address_bar | Add OpenSearch engine from urlbar | browser/browser_add_search_engine.js, browser_contextualsearch_install.js |
| test_added_open_search_engine_default | Added engine set default | search/browser_addSearchEngineFromForm.js |
| test_addon_suggestion | Add-on suggestions | quicksuggest/browser_quicksuggest_addons.js |
| test_addressbar_search_engine_keywords | Keyword/alias engine trigger | browser/browser_keyword.js, browser_tokenAlias.js, browser_action_searchengine_alias.js |
| test_bing/ddg/google_us/google_non_us search codes | Partner SAP tagging in URL | telemetry/browser_search_telemetry_sources.js, _app_provided_and_overridden.js |
| test_clipboard_pref_flip | "Visit from clipboard" pref | browser/browser_clipboard.js |
| test_copied_url_contains_https | Copied URL retains https | browser/browser_copying.js, browser-UrlbarInput/browser_trimURLs.js |
| test_ctrl_enter_completes_link / _fixes_url | Ctrl+Enter canonize domain | browser/browser_canonizeURL.js, browser-autofill/browser_canonize.js |
| test_default_search_provider_change_awesome_bar | Default engine → urlbar placeholder | browser/browser_placeholder.js |
| test_default_search_provider_change_legacy_search_bar | Default engine → search bar | search/browser_searchbar_default.js |
| test_delete_history_entry_via_firefox_suggest_completion_list | Delete result removes history | browser/browser_remove_match.js |
| test_disable_websearch_from_awesome_bar | Web-search pref off | browser/browser_searchSettings.js |
| test_dont_show_search_suggestions_in_private_window | No suggestions in PBM | search/browser_private_search_perwindowpb.js |
| test_google_search_counts_us | SAP search-count telemetry | telemetry/browser_search_telemetry_sources.js |
| test_google_withads_url_bar_us | With-ads impression telemetry | telemetry/browser_search_telemetry_adImpression_component.js |
| test_sap_google_adclick | Ad-click telemetry | telemetry/browser_search_telemetry_sources_ads_clicks.js |
| test_insertion_point_no_search_terms_display | Search-mode empty indicator | browser-searchMode/browser_indicator.js |
| test_no_suggestions_for_empty_query | No suggestions empty query | browser-searchMode/browser_no_results.js |
| test_non_sponsored_topsite_context_menu_option | Top-site tile context menu | browser/browser_top_sites.js, browser_urlbar_contextmenu.js |
| test_open_link_in_new_container_tab | Open link in container tab | browser/browser_urlbar_contextmenu.js (partial) |
| test_paste_and_go_opens_correct_url | Paste-and-Go | browser/browser_pasteAndGo.js |
| test_refresh_firefox_dialog | Refresh-Firefox tip | browser-tips/browser_updateRefresh.js |
| test_search_bar_results_shown_in_a_new_tab | Search-bar submit new tab | search/browser_searchbar_enter.js |
| test_search_engine_result_page_load_on_reload | SERP reload | browser-UrlbarInput/browser_searchTerms.js |
| test_search_engine_selector | One-off engine selection | browser/browser_oneOffs.js |
| test_search_mode_appears_after_input | Switch engine mid-query | browser-searchMode/browser_searchModeSwitcher_searchMode.js |
| test_search_mode_change_tab | Search mode per tab | browser-searchMode/browser_switchTabs.js |
| test_search_mode_cleared_on_engine_removal | Removing engine clears mode | browser-searchMode/browser_engineRemoval.js |
| test_search_mode_exits_correctly | Exit search mode | browser-searchMode/browser_searchModeSwitcher_basic.js |
| test_search_mode_persists_mixed_with_bing | @token ignored in active mode | browser-searchMode/browser_alias_replacement.js |
| test_search_mode_update_on_alias_prefix | Alias prefix enters mode | browser-searchMode/browser_alias_replacement.js |
| test_search_modes_for_sites | Tab-to-search | browser/browser_tabToSearch.js |
| test_search_string_displayed_when_addressbar_unfocused | Persisted term unfocused | browser-UrlbarInput/browser_searchTerms.js |
| test_search_suggestions | Firefox Suggest sponsored/non | quicksuggest/browser_quicksuggest.js |
| test_search_suggestions_can_be_disabled | Suggestion pref | browser/browser_searchSuggestions.js |
| test_search_term_persists | Persisted search terms | browser-UrlbarInput/browser_searchTerms*.js |
| test_server_not_found_error / _pb | DNS-error page + link | browser/browser_redirect_error.js |
| test_suggestion_engine_selection | "@" engine list | browser/browser_tokenAlias.js |
| test_switch_to_existing_tab_when_having_the_same_URL | Switch-to-tab | browser/browser_tabMatchesInAwesomebar.js |
| test_tile_menu_options | Top-site tile actions | browser/browser_top_sites.js |
| test_use_different_search_shortcut_while_already_in_search_mode | Switch engine in-mode | browser-searchMode/browser_alias_replacement.js |
| test_verify_url_after_tab_switch_with_search_mode | URL after tab switch | browser-UrlbarInput/browser_searchTerms_switch_tab.js |
| glean/serp_impression (matrix) | SERP impression telemetry | telemetry/browser_search_glean_serp_event_telemetry_*.js |
| glean/serp_abandonment (matrix) | SERP abandonment telemetry | telemetry/browser_search_telemetry_abandonment.js |

**STARfox-unique:** test_search_bar_display_alpenglow_theme (visual/theme), region-parametrized partner-code matrix (FF uses mock engine).

## 1.2 Tabs / session restore / toolbar & theme (STARfox 39 → ~37 mapped)

| STARfox test | Feature | Matching Firefox test(s) |
|---|---|---|
| test_open_new_tab | New tab via "+" | tabs/browser_addAdjacentNewTab.js, browser_new_tab_url.js |
| test_open_new_tab_keys | New tab via keyboard | tabs/browser_tabkeynavigation.js (partial) |
| test_open_new_tab_via_hyperlink | Open link in new tab | tabs/browser_contextmenu_openlink_after_tabnavigated.js |
| test_open_new_bg_tab_via_mouse_and_keyboard | Middle/Ctrl-click bg tab | tabs/browser_openURI_background.js, browser_window_open_modifiers.js |
| test_active_tab | Active tab highlight/focus | tabs/browser_tabfocus.js, browser_tabswitch_select.js |
| test_list_all_tabs | List-all-tabs menu + overflow | tabs/browser_list_all_tabs_menu_items.js, browser_overflowScroll.js |
| test_navigation_multiple_tabs | Tab strip overflow scroll | tabs/browser_overflowScroll.js |
| test_pin_tab | Pin/unpin single tab | tabs/browser_pinnedTabs.js |
| test_pin_unpin_selected_tabs | Pin/unpin multi | tabs/browser_multiselect_tabs_pin_unpin.js |
| test_change_position_of_pinned_tabs | Reorder pinned | tabs/browser_pinnedTabs.js, browser_tabReorder.js |
| test_close_pinned_tab_via_mouse | Close pinned | tabs/browser_pinnedTabs_closeByKeyboard.js (variant) |
| test_close_tab_through_middle_mouse_click | Middle-click close | tabs/browser_close_tab_by_dblclick.js |
| test_reopen_tab_through_context_menu | Reopen closed tab | tabs/browser_undo_close_tabs.js, sessionstore/browser_undoCloseById.js |
| test_reopen_tabs_through_keys | Ctrl+Shift+T | sessionstore/browser_restoreLastClosedTabOrWindowOrSession.js |
| test_reopen_tab_through_history_menu | Reopen from History menu | customizableui/browser_history_recently_closed.js |
| test_reload_tab_via_keyboard | F5 / Ctrl+R | tabs/browser_tab_label_during_reload.js, customizableui/browser_reload_tab.js |
| test_mute_tabs | Mute/unmute single | tabMediaIndicator/browser_mute.js, tabs/browser_audioTabIcon.js |
| test_play_mute_unmute_tabs_via_toggle | Multi mute/play | tabs/browser_multiselect_tabs_mute_unmute.js |
| test_move_single_tab_via_context_menu | Move + close-to-right/other | tabs/browser_removeTabsToTheEnd.js, browser_removeAllTabsBut.js |
| test_move_multi_selected_tabs | Move multi | tabs/browser_multiselect_tabs_move.js |
| test_group_tabs / test_ungroup_tabs | Create/ungroup tab group | tabs/browser_tab_groups.js, browser_tab_group_menu.js |
| test_edit_tab_groups | Edit group name/color | tabs/browser_tab_group_menu.js |
| test_remove_tab_from_a_group | Remove tab from group | tabs/browser_tab_groups_tabContextMenu.js |
| test_save_and_close_a_tab_group | Save & close group | sessionstore/browser_tab_groups_save_on_window_close.js |
| test_restore_closed_tabs_previous_groups | Restore into group | sessionstore/browser_tab_groups_restore_to_group.js |
| test_hover_tab_preview / test_tab_hover_different_content_type | Tab hover preview | tabs/browser_tab_preview.js |
| test_display_customize_button | Customize button | customizableui/browser_switch_to_customize_mode.js |
| session_restore/test_restore_last_closed_tabs_shortcut | Restore last closed | sessionstore/browser_restoreLastClosedTabOrWindowOrSession.js |
| session_restore/test_restore_multiple_closed_tabs_at_once | Restore multiple | sessionstore/browser_restoreLastActionCorrectOrder.js |
| session_restore/…fx_view_corresponding_section | Recently-closed in Fx View | firefoxview/browser_recentlyclosed_firefoxview.js |
| session_restore/…history_menu_bar | Recently-closed History menu | customizableui/browser_history_recently_closed.js |
| session_restore/…library_menu | Recently-closed Library menu | customizableui/browser_history_recently_closed.js (closest) |
| session_restore/…removed_from_all_history_entries | Restore-all clears lists | sessionstore/browser_closed_objects_changed_notifications_tabs.js |
| theme_and_toolbar/test_installed_theme_enabled | Install AMO theme | profiles/browser_test_current_theme_from_amo.js |
| theme_and_toolbar/test_customize_themes_and_redirect | Built-in themes | customizableui/browser_customizemode_lwthemes.js |

**STARfox-unique:** test_reload_overiding_cache_keys (HTTP cache-header check), test_open_bookmark_in_new_tab.

## 1.3 Security / privacy / networking / notifications / geolocation (STARfox 86 → ~74 UI-level)

| Sub-area | STARfox tests | Matching Firefox test(s) |
|---|---|---|
| ETP / tracking panel | test_blocking_cryptominers, _fingerprinters, _social_media_trackers, cross_site_tracking_cookies*, detected_blocked_trackers, tracking_content_custom_mode, *_subpanel_display_*, trackers_cryptominers_fingerprinters_blocked, no_trackers_detected, etp_toggle_on_off*, etp_panel_displayed_when_*, trackers_counted_correctly, see_all_link*, protection_level_redirect*, privacy_settings_footer_link, clear_cookies_site_data_via_panel, ensure_panel_renders, third_party_content_blocked_pb | protectionsUI/browser_protectionsUI_*.js, siteIdentity/browser_identityPopup_clearSiteData.js |
| Connection / cert / identity | secure_domain_certificate*, connection_secure_second_level, connection_not_secured*, http_lock_icon, mixed_content_warning, certificate_expired, extended_certificate_messaging, tls_v1_2, phishing_and_malware_warnings, http_site, https_enabled_pb, https_first_mode_pb | siteIdentity/browser_identity_UI.js, browser_check_identity_state.js, browser_mixed_passive_content_indicator.js, browser_identityPopup_HttpsOnlyMode.js |
| Private browsing | private_window_from_panelui, open_private_browsing_via_keyboard, open_link_in_private_window, private_browser_password_doorhanger, cookies_not_saved_pb, end_private_session_clears_cookies, cache_is_cleared*, no_cached_file_pb, private_session_history/awesome_bar_exclusion, downloads_from_private_not_leaked, download_list_cleared*, data_clearance_can_be_canceled, sidebar_removed_on_end, undo_close_tab_pb, never_remember_browsing_history | privatebrowsing/browser_privatebrowsing_*.js |
| Permissions / notifications / geo | camera/audio_video/microphone_permissions, screen_share*, deny_screen_capture, deny_geolocation, geolocation_prompt_presence, geolocation_allow_browserleaks, geolocation_shared_via_html5/w3c_api, notifications_displayed, cancel_webextension, webextension_completed_installation | webrtc/browser_devices_get_user_media*.js, permissions/browser_permission_delegate_geo.js, siteIdentity/browser_geolocation_indicator.js, webextensions/browser_permissions_*.js |
| DoH | cloudflare_as_default, default_dns_protection, nextdns/custom_doh_provider, heuristics_disabled_when_trr_mode_2 | doh/browser_remoteSettings_rollout.js, browser_providerSteering.js, browser_throttle_heuristics.js |

**STARfox-unique:** bookmarks-in-PBM (add/remove/toolbar-present), end-private-session-button toolbar customization, passwords_appear_in_firefox_lockwise, copy_clean_link (UI action).

## 1.4 Password manager & form autofill (STARfox 68 → ~60 mapped)

| Sub-area | STARfox tests / coverage | Matching Firefox test(s) |
|---|---|---|
| Doorhanger | save / update / never-save / add-username / username-edit / password-field-only / key-icon / private-browsing-dismiss / insecure | passwordmgr/browser_doorhanger_*.js, browser_exceptions_dialog.js, browser_autocomplete_insecure_warning.js |
| about:logins | add / edit / delete / copy (username, password) / show-hide / search (username, website, password) / origin-link / 5 navigation entry-points / direct-nav | aboutlogins/browser_createLogin.js, browser_updateLogin.js, browser_deleteLogin.js, browser_copyToClipboardButton.js, browser_loginFilter.js, browser_openSite.js, passwordmgr/browser_openPasswordManager.js |
| Primary password (9 tests) | set / change / remove PP; PP gate on reveal, copy, edit, about:logins access; edit-autofill-after-PP-dismissed; no-gen-password-under-PP | aboutlogins/browser_primaryPassword.js, passwordmgr/browser_autocomplete_primary_password.js, browser_osAuthDialog.js |
| Generated passwords (3) | suggest-strong-password from context menu; autosave; edited+generated re-appear in autocomplete | passwordmgr/browser_context_menu_generated_password.js, browser_doorhanger_generated_password.js |
| Login autocomplete / autofill (8) | dropdown on focused field at load; multiple-cred fill; "use saved password" context-menu presence; live-site autofill (Facebook/Google/Reddit/Taobao) | passwordmgr/browser_preselect_login.js, browser_context_menu.js, browser_autofill_after_paint.js |
| CSV export (3) | export passwords.csv; validate contents/columns; export gated by PP | aboutlogins/browser_openExport.js, satchel/megalist/browser_passwords_export_success_notification.js |
| Address autofill (9) | create profile; attribute values (name, street, tel) in dropdown; suggestions; clear; update; enable-disable; private-mode not saved | formautofill/browser_manageAddressesDialog.js, browser_autofill_address_*.js, browser_clearPopulatedForm.js, browser_privacyPreferences.js, browser_submission_in_private_mode.js |
| Credit-card autofill (11) | fill / save / four-fields / suggestions / cvv-not-stored / doorhanger / enable / clear / create / edit / delete / update | formautofill/creditCard/browser_creditCard_doorhanger_*.js, browser_autofill_creditCard_*.js, browser_manageCreditCardsDialog.js, browser_editCreditCardDialog.js |

**STARfox-unique:** live-site logins (Facebook/Google/Reddit/Taobao — incl. Google passkey-in-dropdown), non-ASCII add-login.

## 1.5 Bookmarks / history / downloads / preferences / profiles (STARfox 61 → ~40 mapped)

| Sub-area | STARfox tests / coverage | Matching Firefox test(s) |
|---|---|---|
| Bookmarks | star-button / menu / toolbar add-edit (+ not-saved-realtime variants), folder add/edit, Other Bookmarks add/delete, delete-from-toolbar, open / open-all, open-in-new/private-window, toggle-toolbar | places/browser_bookmark_popup.js, browser_bookmarkProperties_*.js, browser_remove_bookmarks.js, browser_click_bookmarks_on_toolbar.js, browser_library_open_all.js, browser_bookmark_context_menu_contents.js, browser_autoshow_bookmarks_toolbar.js |
| History | in-hamburger-menu (tab/window), open-from-history, pb-not-in-history, clear-all/recent, deleted-page/forget | toolkit/places/browser_visituri*.js, places/browser_forgetthissite.js, places/interactions/browser_interactions_clearHistory.js |
| Downloads | download pdf/apk/mp3/exe/epub + extension checks, delete-in-progress, malicious-warning, panel-open telemetry, change-folder, file-type handler ("always ask", mime, zip) | downloads/browser_basic_functionality.js, browser_downloads_context_menu_delete_file.js, browser_blocked_and_deleted_status.js, browser_downloads_panel_opens.js, preferences/downloads/browser_downloads.js, preferences/applications/browser_filetype_dialog.js |
| Preferences | check-for-updates, clear/manage cookies, never-remember-history, notifications-change, firefox-home-on-launch/new-tabs | preferences/browser_advanced_update.js, siteData/browser_clearSiteData_v2.js, privacy/browser_privacypane_3.js, home/browser_homepage_firefox_home.js |
| Locale | lang-pack via prefs + set-locale | preferences/languages/browser_languages_pane.js |
| Profiles / migration | set-default-profile (about:profiles — weak match to new profiles/browser_activate.js), import-bookmarks Chrome/Edge | migration/browser_do_migration.js, browser_edge_bookmarks_success_strings.js |

**STARfox-unique at this layer:** download telemetry/Glean assertions, cross-browser import via UI, install-unsigned-addon, lang-pack via about:addons.

## 1.6 PDF / print / reader / find / media / zoom (STARfox ~43 → ~35% of areas)

| Sub-area | STARfox tests / coverage | Matching Firefox test(s) |
|---|---|---|
| PDF | open-in-FF, download/save-as (+ form fields/data), navigation, zoom (checkbox/text/radio/dropdown), form fields (checkbox/dropdown/input/prefilled/modify/copy-paste/contextual-menu/clear), add-image, draw/text editor, find-in-pdf | pdfjs/browser_pdfjs_main.js, browser_pdfjs_download_button.js, browser_pdfjs_navigation.js, browser_pdfjs_zoom.js, browser_pdfjs_form.js, browser_pdfjs_editing_contextmenu.js, browser_pdfjs_find.js |
| Printing | print-preview (panel + key), page-number indicator, print-to-pdf | printing/browser_modal_print.js, browser_preview_navigation.js, browser_print_stream.js |
| Reader | enter/exit (button + keys), type controls | reader/browser_readerMode.js, browser_readerMode_textLayoutPref.js |
| Find | search + clear, next/prev/wrap | toolkit/content browser_findbar.js, browser_findbar_marks.js |
| Audio / video | allow/block autoplay, background-tab autoplay + icon, per-site persistence | base/content browser_autoplay_blocked.js, browser_delay_autoplay_media.js, browser_audioTabIcon.js |
| Zoom | menu zoom in/out/reset, ctrl+wheel, default-persists, text-only | base/content browser_zoom_commands.js, browser_mousewheel_zoom.js, browser_default_zoom*.js |

**STARfox-unique:** granular reader Type-panel (char/word spacing, width sliders), autoplay prefs UI, HTML5 `<video>` page controls.

## 1.7 Sidebar / AI / menus / drag&drop / pocket / sync (STARfox ~44 → ~30 mapped)

| Sub-area | STARfox tests / coverage | Matching Firefox test(s) |
|---|---|---|
| Sidebar & vertical tabs (19) | toggle button, fresh-profile button, hide, PBM, switch vertical/horizontal, expand-on-hover (+ right-side / horizontal-disable), pin/unpin, multiselect (pin/move/close), close options (menu/Ctrl+W/middle), multiselect-close (other/above/below), close-on-hover, mute/unmute, duplicate-close, reload, bookmark, reopen-closed, manage-pinned-extensions | sidebar/browser_toolbar_sidebar_button.js, browser_hide_sidebar.js, browser_vertical_tabs.js, browser_sidebar_expand_on_hover.js, browser_sidebar_pinned_tabs.js, tabs/browser_multiselect_tabs_*.js, browser_extensions_sidebar.js |
| AI chatbot / genai (7) | open via context/page menu, choose provider, removal hides entry, summarize (tab menu / sidebar menu / panel × 6 providers), AI killswitch | genai/browser_chat_contextmenu.js, browser_chat_sidebar.js, browser_chat_page.js, browser_genai_init.js |
| Context / tab menus (8 files) | copy/paste/reveal-password, hyperlink open targets, copy-link/paste-and-go, save-page/screenshot/inspect, image actions, new-tab label, tab-menu duplicate/close-right/left/other | base/content browser_contextmenu*.js, tabs/browser_multiselect_tabs_*.js, passwordmgr/browser_context_menu.js |
| Sync / FxA (2) | existing / new FxA sign-in (STARfox uses real stage server) | services/.../browser_fxa_web_channel.js (mocked) |

**STARfox-unique:** entire `drag_and_drop/` clipboard suite (5), real-server FxA E2E, multi-provider live summarize loop. **Pocket (4): skipped, no FF coverage either.**

---

# Part 2 — Missing coverage (Firefox tests it, STARfox does not)

Tagged `[A]` = automation candidate, `[M]` = manual candidate. Ordered roughly by user-facing value within each domain.

## 2.1 Entire features with ZERO STARfox coverage (highest priority)

| Feature | FF tests | Tag | Note |
|---|---|---|---|
| **Picture-in-Picture** | ~85 (`toolkit/components/pictureinpicture`) | A (core) / M (window geometry) | Flagship feature, 0 tests. Start: toggle/open/close, ESC-close, close-pauses-video, toggle-button visibility, player controls, subtitles. |
| **AI Window / Smart Window** | ~100 (`browser/components/aiwindow`) | A | Confirm ship/pref status first. Smoke: open, first-run, smartbar-ask, new-chat, stop-generation. |
| **SelectableProfiles (multi-profile UI)** | ~20 (`browser/components/profiles`) | A | STARfox only has legacy about:profiles. Create/edit/delete/selector/avatar/appmenu/move-tab-to-profile all untested. |
| **Split View (side-by-side tabs)** | ~15 (`tabbrowser` + sessionstore) | A | New feature. Create/close/contextmenu/resize/keyboard-focus. |
| **Bookmarks Library window** | ~30 (`places browser_library_*`) | A | Core management surface — new/move/delete/search/sort/commands, none covered. |
| **Link Preview / Page Assist** | ~10 (`genai`) | A | Hover link preview + opt-in; page assist sidebar. |
| **Real tab drag-and-drop** | ~8 (`tabbrowser/dragdrop`) | M | Reorder/detach/drag-to-pin/drag-to-bookmarks. HTML5 DnD unreliable in WebDriver — smoke manually or targeted action-chain spike. |
| **Cookie banner handling** | ~17 (`cookiebanners`) | A | Auto reject/accept banners; user-facing toggle. |
| **Bounce Tracking Protection** | ~20 (`bouncetrackingprotection`) | A (panel) / M (purge) | protectionsUI entry automatable; purge behavior integration-level. |

## 2.2 Address bar & search

| Gap | Tag | Note |
|---|---|---|
| Quick actions (screenshot, mute, translate, devtools, commands, tab-refocus) | A | Entire surface uncovered. |
| Urlbar keyboard/editing: result-list nav, Tab-key, cut/delete/delete-all, caret position | A | Core interaction touched only indirectly. |
| URL trimming / untrim-on-interaction / formatValue domain highlighting / unsafe-protocol strip on paste | A | Paste sanitization is security-relevant. |
| Autofill dismissal (backspace) + typed / preserve / undo / first-result autofill | A | STARfox covers only adaptive-history autofill. |
| Result types: calculator, unit conversion, rich / trending / recent-search suggestions, best match | A | Simple, high-visibility; trivially assertable. |
| Quick Suggest breadth: block/dismiss, contextual opt-in, MDN, Yelp, weather | A / M | Block/opt-in automatable; realtime/geo may be manual. |
| Result "…" menu (dismiss / manage per result) | A | Per-result menu unverified E2E. |
| One-off context menu / set-default / key-modifiers; search-mode preview / heuristic / local-one-offs / new-window | A | STARfox covers one-off selection but not these. |
| Legacy search bar interactive surface: popup, one-offs, keyboard nav, drag-drop, context menu, removal | A | STARfox only tests default-engine + new-tab + theme. |
| Content-area `Search for <selection>` + visual search | A | Glean covers contextmenu telemetry, not the UX. |
| Engagement telemetry family (n_chars/n_words, selected-action, reenter, exposure) | A | STARfox glean covers impression + abandonment only. |
| SPA / subframe / multi-tab SERP telemetry | M | Deep integration-level; low ROI for Selenium. |
| Trust panel / site security view in urlbar; search tips / interventions | A | STARfox only covers the update/refresh tip. |

## 2.3 Tabs / session / toolbar

| Gap | Tag | Note |
|---|---|---|
| Tab drag-and-drop (reorder, detach, drag-to-window/pin) | M | See 2.1. HTML5 DnD unreliable in WebDriver. |
| Split view | A | See 2.1. |
| Tab Manager / all-tabs panel *actions* (close / drag / group / keyboard) | A | STARfox only opens the list. |
| Multiselect beyond pin/mute/move: close / close-others / close-left/right, duplicate, bookmark, reload, Shift-range, keyboard | A | Broad multiselect gap. |
| Tab groups: keyboard / list / insert-after-current | A | STARfox has group CRUD but not these. |
| Tab groups: a11y (screen-reader semantics) | M | Hard to automate in Selenium. |
| Tab groups: cross-window closed-group restore / undo | A | |
| Full session/window restore: restore-previous-session, undo-close-window, restore-tabless-window | A | STARfox restores tabs, not whole sessions. |
| Session data persistence: form data, scroll positions, sessionStorage, cookies, restore-pinned | A | User-visible after reopening a tab. |
| Customize-mode depth: drag widgets to/from palette, restore-defaults, UI density, flexible-space, toolbar visibility, vertical-tabs-navbar | A | STARfox only adds one widget once. |
| Vertical tabs dedicated coverage (enable / reorder / pin / restore) | A | Only touched inside one group test today. |
| Firefox View beyond recently-closed: Open Tabs, History, search, keyboard nav | A | STARfox uses Fx View only for recently-closed. |
| Firefox View: Synced Tabs | M | Requires FxA sign-in. |
| Ctrl+Tab MRU switching, Ctrl+1..9 select, selectMRUOnClose | A | Common shortcuts, untested. |

## 2.4 Security / privacy / networking / notifications

| Gap | Tag | Note |
|---|---|---|
| **Anti-tracking behavior** (not just panel text): blocking / partitioning of cookies, localStorage, IndexedDB, ServiceWorkers, cache, network | A | Biggest gap (~120 FF tests). STARfox checks only panel text. |
| Storage Access API doorhanger + grant flow | A | User-facing permission doorhanger, no coverage at all. |
| WebRTC sharing lifecycle: indicator, stop-sharing, global mute, tab-switch warning, paused | A | STARfox only covers the initial prompt. |
| RFP observable behavior: spoofed timezone/navigator, canvas randomization, rounded window | A / M | A few E2E checks automatable; full matrix is integration-level. |
| popupNotification security-delay (anti-clickjacking), "remember" checkbox, keyboard nav | A | Security-relevant timing STARfox bypasses. |
| Popup blocker (`popups/browser_popup_blocker*.js`) | A | No popup-blocker coverage. |
| DoH first-run doorhanger (reject → rollback) | A | STARfox covers provider selection, not first-run prompt. |
| Report Broken Site (menu → form → send, anti-tracking data) | A | Menu → form → send flow untested. |
| Notification management: close, do-not-disturb, remove-permission | A | STARfox only fires a notification. |
| Email tracking protection subview; clear-site-data PBM / extensions variants | A | STARfox has only the plain clear-site-data path. |
| Cert-error page UI, HTTPS-Only per-site exception UI, "More Information" cert chain | A | Panel text read, but not these states. |

## 2.5 Password manager & form autofill

| Gap | Tag | Note |
|---|---|---|
| **Address capture / save / edit doorhanger** (`browser_address_doorhanger_*`, `browser_edit_address_doorhanger_*`) | A | Parallels CC doorhanger STARfox already has; addresses only saved via prefs today. |
| **Login import** (CSV + from-browser) | A | STARfox has export but not import (asymmetric). |
| **Breach / vulnerable-password alerts** in about:logins | A | User-visible security banner untested. |
| **Sidebar Passwords (Megalist)** (`satchel/megalist/browser_passwords_*`) | A | Entire newer password UI surface, zero coverage. |
| **Cross-origin / iframe autofill** (CC + login) | A | High security value. |
| HTTP Basic-Auth / proxy prompt save flow; remove-all-logins dialog; login-list sort / errors (duplicate-origin, empty-required) | A | Distinct flows STARfox never exercises. |
| Doorhanger edges: multipage-form, reveal-in-doorhanger, httpsUpgrade, target=_blank / window.open / cross-frame | A | Multipage + reveal are common; rest are edge cases. |
| CC insecure-form + anti-clickjacking | A | Mirrors login insecure-warning STARfox already has. |
| CC OS-auth reveal; CC decryption failure | M | OS-native auth / corrupt-storage setup. |
| Firefox Relay email-mask; about:logins tab / keyboard a11y | M | Needs FxA/Relay account; a11y focus order. |
| Plain satchel form-history autocomplete (non-login / non-CC) | A | Saved form-history entries covered by neither suite. |

## 2.6 Bookmarks / history / downloads / preferences / profiles

| Gap | Tag | Note |
|---|---|---|
| SelectableProfiles + Bookmarks Library | A | See 2.1 (entire features, zero coverage). |
| Bookmark tags (add/remove/bulk); cut/copy/paste bookmarks; bookmark-all-tabs; bookmarks/history **sidebar** search+open; HTML/JSON backup export-import | A | Discrete scriptable features; sidebar surface untouched. |
| Bookmarks toolbar drag / reorder / chevron-overflow | M | Drag/drop fragile in Selenium. |
| Downloads: pause/resume, keyboard nav/focus, "always open similar files", about:downloads + Library downloads view, go-to-download-page | A | STARfox is panel-only today. |
| Downloads: overwrite / temp-file, taskbar progress / autohide | M | Filesystem / OS-integration behavior. |
| **Preferences — Search pane** | A | Default engine, add/reorder/remove engines, suggestions. Large, scriptable. |
| **Preferences — Privacy/ETP beyond cookies** (content-blocking customize, DoH, HTTPS-only, GPC, sanitize-on-shutdown) | A | ETP redesign needs FX153+ (see memory). |
| **Preferences — Home** (custom-homepage/wallpaper/personalization), **Security + password-management**, **AI features** (new) | A | Major panes STARfox doesn't touch. |
| Preferences — Networking/proxy, Sync pane, prefs-search framework / fonts / colors / performance / experimental | M | Env-dependent / needs account / framework-level. |
| Profiles migration: import passwords (Chrome/Windows), Safari import (mac), migration wizard flow (entrypoints/cancel/no-browsers), file-based (HTML/CSV) import | A | STARfox imports bookmarks only. |
| Locale: website-language ordering / Accept-Language fallback UI | A | STARfox installs a pack but not the ordering UI. |

## 2.7 PDF / print / reader / find / media / zoom

| Gap | Tag | Note |
|---|---|---|
| Picture-in-Picture | A / M | See 2.1 (~85 FF tests, 0 STARfox). |
| **Print settings controls** (copies, page-range, margins, scaling, duplex, paper size, orientation) + print-selection, simplified/reader print, destination change/sort, cancel/close, context-menu/frame print | A | Modal already automated — high value/effort ratio. |
| PDF depth: fullscreen/presentation, document properties, highlight/comment annotations, digital signature, pages organize (rotate/delete/reorder), login-autofill into PDF form | A | STARfox has draw/text/image editor but not these. |
| PDF: alt-text / AI / HCM / caret-browsing | M | Accessibility / ML-gated flows. |
| Reader: color-scheme / theme controls, reading-time + scroll-save, local-file reader | A | STARfox Type panel does font/size/spacing, not themes. |
| Reader: tab-navigation / pinned-tab reuse | M | |
| Find: Highlight-All + Match-Case / Whole-Word / Diacritics modifiers, quick-find ("/" and "'") | A | STARfox tests only basic search + nav. |
| Find: hidden / before-match / hidden-frame find | M | Requires special DOM fixtures. |
| Audio: tab mute/unmute via sound icon + persistence, multiselect + global mute | A | STARfox has autoplay but no mute-toggle coverage. |
| Audio: media wakelock / background-video suspend | M | Timing / power-state behavior. |
| Zoom: **site-specific zoom persistence** (per-origin, image, video), image zoom across tab-switch, scroll-to-text-fragment | A | STARfox covers default zoom, not per-site memory. |
| Zoom: tab-switch flicker / tooltip zoom | M | Visual/rendering timing. |

## 2.8 Sidebar / AI / menus / sync

| Gap | Tag | Note |
|---|---|---|
| AI Window / Link Preview / Page Assist | A | See 2.1 (confirm ship/pref status first). |
| **Sidebar tool panels** (Bookmarks, History, Synced Tabs, Open Tabs) | A | STARfox tests the strip, never the panels. |
| Sidebar behavior: resize / max-width / splitter, escape-to-collapse, launcher hidden/restore | A | High-frequency interactions, zero coverage. |
| Sidebar behavior: fullscreen, a11y | M | Fullscreen transitions flaky; a11y trees awkward in Selenium. |
| Chat shortcuts / prompts beyond Summarize | A | STARfox only exercises "Summarize". |
| Chat-sidebar permissions | M | Permission prompts. |
| Context menu: spellcheck, add-search-engine / search-selection, keyboard-driven context menu | A | Complements STARfox's mouse-only menu tests. |
| Context menu: send-tab / send-page, cross-boundary / iframe selection, OS share sheet | M | Needs second synced device / edge cases / OS sheet. |
| **Sync preferences UI**: chooseWhatToSync, sync-settings, sync-disabled, account visibility; sign-in / avatar CTA variants; synced tabs in Fx View / menu | A | STARfox only does sign-in, not the settings surface. |
| Sync pairing (QR / pair another device) | M | Needs a second device. |

---

## Recommended prioritization (top 10 automation targets)

1. **Picture-in-Picture** core lifecycle — flagship feature, 0 tests.
2. **Print settings controls** — modal already automated; huge coverage-per-effort.
3. **SelectableProfiles** multi-profile UI — entirely new, user-facing, 0 tests.
4. **Bookmarks Library window** — core management surface, 0 tests.
5. **Search preferences pane** — large scriptable pane, 0 tests.
6. **Address capture doorhanger** + **login import** — close asymmetric gaps in a suite STARfox already owns deeply.
7. **Anti-tracking behavioral checks** — verify storage/cookies actually blocked, not just panel text.
8. **Sidebar tool panels** (Bookmarks/History/Synced/Open Tabs) — strip is covered, panels are not.
9. **Site-specific zoom persistence** + **tab mute via sound icon** — small, high-frequency UX.
10. **Full session/window restore** + **session data persistence** (form/scroll) — common recovery flows.

**Confirm-before-investing (may be behind prefs/Nimbus or need accounts):** AI Window, Split View, Link Preview, Sync preferences (needs FxA), Relay, Safari import (mac-only).

**Protect (STARfox-unique, no FF analog):** live-site password autofill, real per-region search codes, real-server FxA, download telemetry, clipboard copy/paste web-editor suite.

