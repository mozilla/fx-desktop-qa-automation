# STARfox ↔ Firefox Desktop Test Coverage Comparison

**Generated:** 2026-07-14 — *LLM-generated analysis; all figures are approximations and reflect a point-in-time snapshot. Re-validate before acting on specific numbers.*
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

---
---

# Part 3 — MANUAL Test Suite (`manual_tests/`) ↔ Firefox Tree Overlap

> **Different dataset from Parts 1–2.** Parts 1–2 compare the ~395 **automated** STARfox Selenium tests
> (`tests/*/test_*.py`) to the tree. **Part 3 compares the full MANUAL TestRail corpus** exported at
> `manual_tests/all_cases.json` — **10,736 manual cases across 103 TestRail suites** — to the automated tests
> that live inside the [mozilla-firefox/firefox](https://github.com/mozilla-firefox/firefox) tree.
>
> **Generated:** 2026-07-23 — *LLM-generated analysis. Manual-side counts are exact (parsed from JSON); Firefox
> tree file counts are point-in-time snapshots verified on searchfox.org/mozilla-central and drift release-to-
> release. Re-validate before acting on specific numbers.*
>
> **Question answered (per request):** which in-tree tests overlap with the manual suite, specifically *which tree
> tests are covered — in terms of integration / user-flow — by the manual tests*, plus a categorization of tree
> tests by type (unit / integration / system / …).

## 3.0 Method & sources (Part 3)

- **Manual side:** `manual_tests/all_cases.json` parsed directly — 10,736 cases, 103 suites, mapped into 80+
  feature areas. Suite names in quotes were confirmed against this repo's `tests/**/conftest.py` `suite_id`
  tuples; others inferred from case titles.
- **Tree side:** test-directory paths, real file names, and framework/manifest conventions verified live on
  [searchfox.org/mozilla-central](https://searchfox.org/mozilla-central/) and
  [firefox-source-docs](https://firefox-source-docs.mozilla.org/testing/automated-testing/index.html) — not recalled.
- **Matching level:** feature / user-capability, same as Parts 1–2.

## 3.1 Executive summary (Part 3)

The manual suite is almost entirely **front-end / UI functional testing** — a human clicking Firefox Desktop
chrome (toolbars, menus, `about:` pages, dialogs, panels) on real builds and real websites. In the tree,
**exactly one automated suite is the true analog: Mochitest browser-chrome (`browser_*.js`)**, with
**Marionette / firefox-ui functional** as a secondary out-of-process analog for restart-dependent flows.
Everything else in the tree (xpcshell, mochitest-plain, web-platform-tests, reftests, GTest, Talos/Raptor) tests
layers below or beside the manual suite and overlaps only weakly.

Classifying every manual case by strength of overlap with the tree's tests:

| Overlap with tree tests | Manual cases | Share | Meaning |
|---|---:|---:|---|
| **STRONG** — a browser-chrome integration suite exercises the same UI flow | 4,654 | 43.3% | Same feature, same altitude |
| **PARTIAL** — some browser-chrome coverage, manual goes wider (locales, real sites, restart, policy matrices) | 3,742 | 34.9% | Overlap exists but incomplete on one side |
| **WEAK** — tree covers only at unit / content / rendering level, not as a UI flow | 2,056 | 19.2% | Manual tests the chrome UX; tree tests the engine/DOM/pixels |
| **NONE** — no live tree coverage at all | 284 | 2.6% | Removed features, 3rd-party integrations, placeholder suites |

**Headline conclusions**

1. **~43% of manual cases have a direct integration-test counterpart in the tree** (browser-chrome): Passwords,
   Preferences, Bookmarks, Downloads, Form Autofill, Tabs, Firefox View, Sidebar, Screenshots, Reader View, Site
   Identity, Onboarding, Translations, Find/PDF, Session Restore, Profiles, GenAI, urlbar core flows.
2. **The tree's integration tests are a *subset* of the manual suite, not a superset.** Where areas map, the tree
   tests the *core mechanic* deterministically; the manual suite re-verifies that mechanic **plus** localization,
   real third-party sites, OS/installer permutations, screen-reader (NVDA) flows, visual/Figma design compliance,
   and cross-restart/update sequences — dimensions the tree deliberately excludes.
3. **The tree is dominated by unit + standards tests the manual suite never touches**, and vice versa. The suites
   are **complementary, not redundant**; the 43% STRONG band is where they genuinely re-test the same thing.
4. **A few manual areas map to *nothing* in the current tree:** Shopping / Review Checker (Fakespot shut down
   2025-06-10, `browser/components/shopping/` removed), third-party antivirus compatibility, Windows Recall
   privacy, and placeholder/junk suites.

## 3.2 Firefox tree test-type taxonomy (categorization by test type)

*This is the "categorize the test type" section requested. It classifies every automated framework in the
mozilla-central tree and states which ones can overlap with a manual UI suite at all.*

| # | Framework | File / manifest convention | Runtime context | **Test-type category** | Overlaps manual UI suite? |
|---|---|---|---|---|---|
| 1 | **xpcshell** | `test_*.js` + `xpcshell.toml`, `test/unit/` | Bare JS/XPCOM shell, parent process, chrome privileges, **no window/DOM** | **UNIT** — JS/XPCOM backend components in isolation | No — no UI |
| 2 | **Mochitest plain** | `test_*.html` + `mochitest.toml` | Web content in a child process (real page DOM), `SpecialPowers` for privileged reach | **INTEGRATION (web-content / DOM APIs)** | Rarely — tests web pages, not chrome |
| 3 | **Mochitest chrome** | `test_*.xhtml` + `chrome.toml` | Privileged (chrome) JS scope, no full browser harness | **INTEGRATION (privileged widgets)** | Secondary — isolated widgets, not end-user flows |
| 4 | **Mochitest browser-chrome** | **`browser_*.js`** + **`browser.toml`** | **Inside a live Firefox window, chrome scope, full UI** (`gBrowser`, chrome document, `BrowserTestUtils`) | **INTEGRATION / partial SYSTEM (front-end)** | **YES — the primary analog to manual UI testing** |
| 5 | **Mochitest a11y** | `test_*.html` + `a11y.toml`, under `accessible/` | Chrome scope, single-process (no Fission) | **INTEGRATION (accessibility tree/API)** | Partially — a11y API, not AT/NVDA flows |
| 6 | **Marionette** | `test_*.py` (Python), `testing/marionette/` + per-component `tests/marionette/` | Remote protocol driving **out-of-process, full Firefox** (chrome + content) | **SYSTEM / END-TO-END (front-end capable)** | **YES — secondary analog; restart/session flows** |
| 7 | **Firefox UI functional** | Python, `testing/firefox-ui/tests/functional/`, `./mach firefox-ui-functional` | Marionette + firefox-puppeteer POM; full browser, can restart | **SYSTEM / END-TO-END (front-end)** | **YES — closest in *kind* to this repo's WebDriver automation** |
| 8 | **Web-platform-tests (WPT)** | `testing/web-platform/tests/` (+ `meta/`) | Content-process web execution, cross-browser | **STANDARDS-COMPLIANCE** | No — spec conformance, not chrome |
| 9 | **Reftests / crashtests** | `reftest.list` / `crashtests.list` | 800×1000 render + pixel compare / load-without-crash | **RENDERING** / robustness | No — pixels & stability, not behavior |
| 10 | **Talos / Raptor / mozperftest** | `testing/talos`, `testing/raptor`, `testing/mozperftest` | Launch real browser, measure timings | **PERFORMANCE** | No — measures, doesn't assert UX |
| 11 | **GTest (C++) / rusttests** | auto-registered, `FINAL_LIBRARY='xul-gtest'`, `mach gtest` | C++ in libxul, terminal, no services | **UNIT (native code)** | No — no UI |
| 12 | **Telemetry / Glean (FOG)** | not a runtime — `testGetValue()`/`testResetFOG()` inside the suites above | inherits host suite | assertion pattern, inherits host category | Only via its host browser-chrome test |

**Only two tree suites meaningfully overlap the manual corpus:** **#4 browser-chrome** (dominant, in-process,
granular chrome-UI assertions) and **#6/#7 Marionette / firefox-ui functional** (out-of-process, whole-application,
restart-capable — architecturally closest to this repo's own POM design). All other tree tests sit at an altitude
the manual suite never operates at.

**How the tree's own tests distribute by type (qualitative):** largest by file count = web-platform-tests
(*standards*, no manual overlap); most prevalent Firefox-authored = xpcshell (*unit*) + mochitest-plain (*content
integration*), little/no manual overlap; most manual-relevant = browser-chrome under `browser/` and parts of
`toolkit/` (thousands of files); rendering/robustness = reftests/crashtests (no overlap); native units = GTest
(no overlap).

## 3.3 Manual suite profile

10,736 cases / 103 suites. By TestRail case type the corpus is overwhelmingly functional: Functional (~8,769),
"Other" (~583), Smoke (~814), Accessibility (~272), plus small numbers of Performance/Regression/Usability/custom.
In practice **every suite is a human-driven UI or system test — there are no unit tests on the manual side.**

Top feature areas by manual case count (consolidated from the 103 suites; full index in §3.8):

| Feature area | Manual cases | Representative manual suites |
|---|---:|---|
| Address Bar / URL bar (+ UI redesign, QR) | 1,314 | "Address Bar 138+", urlbar dropdown redesign, urlbar CSS |
| New Tab / Pocket / customization / top sites | 862 | "Pocket New Tab", HNT customize & wallpapers, weather, frecency |
| Backup & Restore | 828 | Restore Dialog, backup/restore from preferences/onboarding/OneDrive |
| Settings / Preferences (+ design) | 810 | "Preferences", Passwords&Autofill page design, Home&Startup redesign |
| Enterprise Policies (+ installer/update/GenAI policy) | 557 | search engines via `policies.json`, autoupdate policy, block GenAI |
| Passwords / Logins | 465 | "Password manager" (about:logins), saved-credentials autofill dropdown |
| Media / Site Compatibility | 439 | media top-sites playback, BBC/Netflix/Facebook glitch bugs |
| Site Identity / Connection | 354 | "Security and Privacy" lock icon, mixed content |
| UI / Visual redesign (NOVA) | 333 | NOVA chrome design, Smart Window Switcher styling |
| Bookmarks / Places | 308 | Bookmarks Toolbar, Share Folder |
| Onboarding (+ ToU) | 314 | Easy Setup, Terms of Service onboarding |
| Search flows | 276 | Google urlbar/searchbar per-locale, default engine dropdown |
| Find in page / PDF | 242 | findbar, pdf.js find/navigation |
| Downloads | 224 | cancel/retry, drag&drop, truncation |
| Form Autofill | 222 | address & credit-card capture/fill |
| Experiments / Nimbus | 219 | Enroll/Rollout, about:studies |
| Tabs (+ Tab Notes) | 203 | "Tabbed Browser", drag/reorder, rename, tab notes |
| GenAI | 190 | AI window onboarding, chatbot sidebar, opt-in |
| DevTools | 184 | inspector, horizontal tabs |
| Firefox View | 180 | about:firefoxview cards/states |
| Themes / Toolbar | 177 | default/dark/light themes, title bar/toolbars |
| Installer / NVDA-install (Win/Linux) | 366 | Windows installer, rpm/Fedora, NVDA install |
| Sidebar | 105 | enable/resize, panels, vertical tabs |
| Session Restore | 67 | restore tabs/windows, pinned tabs |

## 3.4 STRONG overlap (43.3%) — same feature, same altitude

Tree paths & example files verified on searchfox.

| Manual area (cases) | Tree test directory | Framework / type | Verified example files |
|---|---|---|---|
| Passwords / Logins (465) | `browser/components/aboutlogins/tests/browser/` (~32) + `toolkit/components/passwordmgr/test/browser/` (~68–81) | browser-chrome (INTEGRATION) + xpcshell unit | `browser_createLogin.js`, `browser_deleteLogin.js`, `browser_loginFilter.js`, `browser_doorhanger_save_password.js`, `browser_osAuthDialog.js` |
| Settings / Preferences (527) | `browser/components/preferences/tests/` + ~20 pane subdirs (`privacy/`,`home/`,`search/`,`sync/`,`etp/`,…) | browser-chrome (INTEGRATION) | `browser_about_settings.js`, `browser_appearance_pane.js`, `browser_subdialogs.js`, `browser_open_migration_wizard.js` |
| Bookmarks / Places (308) | `browser/components/places/tests/browser/` (135+) | browser-chrome (INTEGRATION) | `browser_bookmark_add_tags.js`, `browser_autoshow_bookmarks_toolbar.js`, `browser_bookmark_backup_export_import.js`, `browser_bookmark_context_menu_contents.js` |
| Downloads (224) | `browser/components/downloads/test/browser/` (~39–48) | browser-chrome (INTEGRATION) + xpcshell unit | `browser_downloads_panel_opens.js`, `browser_downloads_pauseResume.js`, `browser_downloads_panel_context_menu.js`, `browser_downloads_keynav.js` |
| Form Autofill (222) | `browser/extensions/formautofill/test/browser/` (~53; `address/`,`creditCard/`) | browser-chrome (INTEGRATION) | `browser_address_doorhanger_display.js`, `browser_creditCard_doorhanger_action.js`, `browser_editCreditCardDialog.js`, `browser_creditCard_osAuth.js` |
| Tabs (203) | `browser/components/tabbrowser/test/browser/{tabs,dragdrop,…}` (200+) | browser-chrome (INTEGRATION) | `browser_pinnedTabs.js`, `browser_tab_dragdrop.js`, `browser_multiselect_tabs_reorder.js`, `browser_tab_groups.js` |
| Firefox View (180) | `browser/components/firefoxview/tests/browser/` (28) | browser-chrome (INTEGRATION) | `browser_firefoxview.js`, `browser_opentabs_firefoxview.js`, `browser_syncedtabs_firefoxview.js`, `browser_history_firefoxview.js` |
| Sidebar (105) | `browser/components/sidebar/tests/{browser,marionette}/` (49 + 4) | browser-chrome + marionette | `browser_vertical_tabs.js`, `browser_customize_sidebar.js`, `browser_sidebar_expand_on_hover.js`; `test_initialize_vertical_tabs.py` |
| Screenshots (48) | `browser/components/screenshots/tests/browser/` (~35) | browser-chrome (INTEGRATION) | `browser_test_element_picker.js`, `browser_screenshots_test_full_page.js`, `browser_screenshots_drag_test.js` |
| Reader View (8) | `toolkit/components/reader/tests/browser/` (~19) | browser-chrome (INTEGRATION) | `browser_readerMode.js`, `browser_readerMode_menu.js`, `browser_readerMode_colorSchemePref.js` |
| Site Identity / Connection (354) | `browser/base/content/test/siteIdentity/` (~40) | browser-chrome (INTEGRATION) | `browser_check_identity_state.js`, `browser_identity_UI.js`, `browser_csp_block_all_mixedcontent.js`, `browser_identityPopup_HttpsOnlyMode.js` |
| ETP / Privacy (13) | `browser/base/content/test/protectionsUI/` (~25) | browser-chrome (INTEGRATION) | `browser_protectionsUI.js`, `browser_protectionsUI_fingerprinters.js`, `browser_protectionsUI_cookie_banner.js` |
| Onboarding (+ ToU) (314) | `browser/components/aboutwelcome/tests/browser/` (~24–28) + `browser/components/asrouter/tests/browser/` (30) | browser-chrome (INTEGRATION) | `browser_aboutwelcome_multistage_mr.js`, `browser_aboutwelcome_multiselect.js`, `browser_feature_callout.js`, `browser_multistage_spotlight.js` |
| Find in page / PDF (242) | `toolkit/content/tests/browser/` (findbar, 7) + `toolkit/components/pdfjs/test/` (60+) | browser-chrome (INTEGRATION) | `browser_findbar.js`, `browser_findbar_marks.js`; `browser_pdfjs_find.js`, `browser_pdfjs_navigation.js`, `browser_pdfjs_zoom.js` |
| Translations (40) | `browser/components/translations/tests/browser/` (150+) | browser-chrome (INTEGRATION, mocked engine) | `browser_translations_full_page_panel_basics.js`, `browser_translations_select_context_menu_*`, `browser_translations_about_preferences_manage_downloaded_languages.js` |
| Session Restore (67) | `browser/components/sessionstore/test/` (150+) | browser-chrome (INTEGRATION) | `browser_394759_basic.js`, `browser_closed_tabs_windows.js`, `browser_firefoxView_restore.js` |
| Profiles (56) | `browser/components/profiles/tests/browser/` (22) + `toolkit/profile/test/` | browser-chrome (INTEGRATION) + xpcshell unit | `browser_create_profile_page_test.js`, `browser_edit_profile_test.js`, `browser_test_profile_selector.js`, `browser_fxa_menu_profiles.js` |
| Private Browsing (17) | `browser/components/privatebrowsing/test/browser/` | browser-chrome (INTEGRATION) | private-window UI tests |
| GenAI (175) | `browser/components/genai/tests/browser/` (18) (+ `browser/components/aiwindow/`) | browser-chrome (INTEGRATION) | `browser_chat_sidebar.js`, `browser_chat_shortcuts.js`, `browser_link_preview.js`, `browser_page_assist_sidebar.js` |
| Permissions (+ geo) (43) | `browser/base/content/test/permissions/`, `.../siteIdentity/browser_geolocation_indicator.js` | browser-chrome (INTEGRATION) | permission prompt / indicator tests |
| Address Bar / URL bar (1,068) | `browser/components/urlbar/tests/browser*/` (hundreds) | browser-chrome (INTEGRATION) + xpcshell `unit/` (125+) | `browser-autofill/`, `browser-searchMode/`, `browser-quickactions/`; `unit/test_autofill_adaptiveHistory.js` |

## 3.5 PARTIAL overlap (34.9%) — tree tests the core, manual tests wider

| Manual area (cases) | Tree test directory | Why only partial |
|---|---|---|
| Backup & Restore (828) | `browser/components/backup/tests/browser/` (9 browser-chrome) + `xpcshell/` (46 unit) + marionette | Manual suite is enormous, dominated by restore-**dialog** UI states / OneDrive / onboarding entry points; tree has ~9 UI tests and puts its weight into per-resource archive/encryption **unit** tests |
| New Tab / Pocket / customization (862) | `browser/extensions/newtab/test/browser/` (27) + Jest units + `browser/components/topsites/` | Tree renders newtab & top sites, but manual covers per-**locale** UI (US/GB/DE…), wallpapers, weather, sponsored tiles that tree covers via React **Jest units** or not at all |
| Search flows (276) | `browser/components/search/test/browser/` (~47) + `toolkit/components/search/tests/xpcshell/` (~90 unit) | Tree tests search-UI mechanics + service internals; manual tests **result quality across real engines/locales** the tree can't assert |
| Enterprise Policies (557) | `browser/components/enterprisepolicies/tests/browser/` (~70) + `xpcshell/` | Tree applies a policy then asserts effect (good per-policy overlap); manual covers a much broader **policy matrix**, MSI enterprise client install, cross-product deployment |
| DevTools (184) | `devtools/client/**/test/` (large browser-chrome/mochitest) | Extensive tree coverage, but manual focuses on inspector UX & new horizontal-tabs layout; mapping is many-to-many, not 1:1 |
| Experiments / Nimbus (219) | `toolkit/components/nimbus/test/`, `browser/components/asrouter/tests/` | Enrollment/targeting at unit + some browser level; manual covers real enroll/rollout, about:studies, safe-mode/PBM permutations |
| Network / Proxy / DoH (98) | `toolkit/components/doh/test/browser/` (14) + `netwerk/**` xpcshell units | DoH doorhanger/rollout is browser-chrome; proxy/DNS config largely OS-level + unit |
| Content blocking (49) | `toolkit/components/antitracking/test/browser/` (170+) | Overlaps on tracker-page blocking, but many tree assertions are storage/cookie-**API** level, not the manual URL-block UX |
| Anti-fingerprinting / RFP (10) | `toolkit/components/resistfingerprinting/tests/{browser,xpcshell,gtest}/` | Some browser-chrome; WebGL/vendor-randomize verified mostly at unit/gtest level |
| Themes / Toolbar (177) | `browser/themes/**`, `browser/components/customizableui/test/` | Customization is browser-chrome; theme visual correctness is largely manual/reftest |
| Migration (64) | `browser/components/migration/tests/{browser,unit}/` | Wizard flow tested; **IE / legacy-profile** migration and `rust_migration` telemetry partly manual/OS-specific |
| FxA / Sync (26) | `services/sync/tests/`, `browser/components/**/fxaccounts` | Sync engine has heavy xpcshell; real account create/recovery needs live servers → manual |
| Software Update (17) | `toolkit/mozapps/update/tests/{browser,marionette,unit_*}/` (120+ browser) | About-dialog/doorhanger UI is browser-chrome (strong mechanic); full download→stage→restart and **language-pack** update are marionette/manual |
| Notifications (56) | `toolkit/components/**` alerts/notifications (browser + xpcshell) | Web notifications/alerts partly covered; push + OS-native alert delivery partly manual |
| Context menu (77) | scattered `browser_*context_menu*.js` across components | Covered piecemeal per feature; no single manual↔tree mapping |
| Drag & Drop / File handling (42) | `browser/components/tabbrowser/test/browser/dragdrop/`, file-handler tests | Tab/link drag covered; file-hosting drag/paste-image via real web apps is manual |
| Keyboard shortcuts (40) | scattered browser-chrome | Core shortcuts covered; customization matrix partly manual |
| Add-ons (Linux) (8) | `toolkit/mozapps/extensions/test/` | Install/manage covered; GNOME-extension host integration is manual |

## 3.6 WEAK overlap (19.2%) — tree covers only below the UI

| Manual area (cases) | Nearest tree tests | Test type | Why weak |
|---|---|---|---|
| Media / Site Compatibility (439) | `dom/media/test/` mochitest-plain, reftests | INTEGRATION (content) / RENDERING | Manual plays **real third-party sites** (BBC/Netflix/Facebook/Discord/Jitsi); tree uses synthetic ClearKey/CENC assets — no site-compat overlap |
| UI / Visual redesign — NOVA (333) | reftests; some `browser_appearance_*` | RENDERING / limited browser-chrome | Figma/pixel design compliance & border-radius-per-OS are manual/visual; tree asserts behavior not appearance |
| Settings (design) (283) | `preferences/tests` (behavioral) | INTEGRATION (behavior only) | Manual verifies redesign layout/zoom/high-contrast appearance; tree asserts control behavior |
| Address Bar UI redesign (220) | `urlbar/tests` (behavioral) | INTEGRATION (behavior only) | Dropdown redesign/positioning/zoom is visual QA |
| Accessibility / NVDA install (145) | `accessible/tests/mochitest/` a11y | INTEGRATION (a11y API) | Tree tests the a11y **tree/API**; manual drives real **NVDA** + installer — no overlap |
| Installer / Uninstaller (Win + Linux) (221) | `browser/installer/**`, `toolkit/mozapps/installer/**` | packaging / limited | Real install/uninstall/UAC/rpm/MSIX are OS-integration manual tests; tree mostly builds packages |
| Text fragments (114) | `dom/base/test/` mochitest-plain (~3) + WPT | INTEGRATION (DOM API) / STANDARDS | Tree parses directives/ranges at DOM level; manual "click highlight → copy link" UX only lightly covered |
| WebRTC / Media conferencing (87) | `dom/media/**` mochitest, WPT | INTEGRATION (content) / STANDARDS | Real Discord/Jitsi/Facebook AV sessions are manual |
| Scrolling / Rendering (94) | reftests, APZ mochitests | RENDERING | Smoothness/APZ on real pages is manual/perf |
| DRM / EME (72) | `dom/media/test/test_eme_*.html` | INTEGRATION (content) | ClearKey stands in; **Widevine** (real Google CDM) not exercised in-tree → manual only for real DRM |
| Sandbox / GPU (21) | `security/sandbox/**` gtest/xpcshell | UNIT (native) | GPU-process/sandbox verified at native level |
| Image rendering / compat (18) | reftests, image mochitests | RENDERING | jpg/gif correctness is reftest/manual-visual |
| Crash Reporter (6) | `toolkit/crashreporter/test/` | UNIT + limited | Crash submission UX partly manual |
| Telemetry / DBA (3) | Glean patterns inside suites | assertion pattern | Pre-release ping collection verified indirectly |

## 3.7 NONE — no live tree coverage (2.6%)

| Manual area (cases) | Status |
|---|---|
| Shopping / Review Checker (102) | **Removed from tree.** Fakespot/Review Checker shut down 2025-06-10; `browser/components/shopping/` no longer exists → zero current automated coverage. |
| 3rd-party / Antivirus compatibility (86) | External products (AV install/interop). Inherently un-automatable in-tree. |
| Privacy / Windows Recall (10) | Windows Recall screenshot-exclusion behavior; no in-tree suite. |
| Placeholder / Junk (30) | Suites like "test111", "Click Me" demo, "Attention message" demo — not real product tests. |
| Misc / Lists, UI/misc, Branding (56) | Ambiguous or non-product (branding of signed builds, unclassified). |

## 3.8 Which tree tests are "covered" by the manual integration suite

Reframing the core question — *are there tests in the tree the manual suite covers in terms of integration?* —
**yes, and the relationship is consistent**: for every STRONG-overlap area in §3.4, the tree's **browser-chrome
integration tests and the manual cases test the same user flow at the same altitude.** These tree browser-chrome
suites are functionally re-covered (redundantly, from an external/manual perspective) by the manual corpus:

- `browser/components/aboutlogins/tests/browser/` + `toolkit/components/passwordmgr/test/browser/` ⟷ Password manager manual (465)
- `browser/components/preferences/tests/` ⟷ Preferences manual (527)
- `browser/components/places/tests/browser/` ⟷ Bookmarks manual (308)
- `browser/components/downloads/test/browser/` ⟷ Downloads manual (224)
- `browser/extensions/formautofill/test/browser/` ⟷ Form Autofill manual (222)
- `browser/components/tabbrowser/test/browser/` ⟷ Tabbed Browser + Tab Notes manual (203)
- `browser/components/firefoxview/tests/browser/` ⟷ Firefox View manual (180)
- `browser/components/sidebar/tests/browser/` ⟷ Sidebar manual (105)
- `browser/components/screenshots/tests/browser/` ⟷ Screenshots manual (48)
- `browser/base/content/test/siteIdentity/` + `.../protectionsUI/` ⟷ Security/Privacy + ETP manual (367)
- `browser/components/translations/tests/browser/` ⟷ Translations manual (40)
- `toolkit/content/tests/browser/` (findbar) + `toolkit/components/pdfjs/test/` ⟷ Find + PDF manual (242)
- `browser/components/sessionstore/test/` ⟷ Session Restore manual (67)
- `browser/components/profiles/tests/browser/` ⟷ Profiles manual (56)
- `browser/components/aboutwelcome/tests/browser/` + `browser/components/asrouter/tests/browser/` ⟷ Onboarding manual (314)
- `browser/components/genai/tests/browser/` ⟷ GenAI manual (190)
- `browser/components/urlbar/tests/browser*/` ⟷ Address Bar manual core flows (within 1,068)

**Direction of the overlap (important):** the tree's integration tests are the *narrower* set — they verify the
core mechanic deterministically ("the save-password doorhanger appears and stores the login"). The manual cases
re-verify that mechanic **plus** the dimensions browser-chrome intentionally excludes:

| Dimension the manual suite adds on top of the tree's integration tests | Examples |
|---|---|
| **Real websites / content compatibility** | playback on BBC/Netflix, autofill on live retail forms, find on a real PDF |
| **Localization** | New Tab UI per locale (US/GB/DE), search handoff per Google locale, language packs |
| **OS / installer integration** | Windows UAC, MSIX, rpm/Fedora, desktop-shortcut toggle, uninstaller survey |
| **Assistive tech** | NVDA-driven install and navigation |
| **Visual / design compliance** | NOVA redesign, Figma border-radius per macOS version, high-contrast, zoom levels |
| **Cross-restart / update sequences** | background update, staged update resume, language-pack update not bricking the browser |
| **Third-party interop** | antivirus install/cert behavior, OneDrive backup restore |

Marionette / firefox-ui functional tests (`testing/firefox-ui/`, plus per-component `tests/marionette/` in sidebar,
backup, profiles, update) are the *architectural* twin of this repo's WebDriver automation and cover the
restart/session-persistence slice — but they are a small suite, so most manual↔tree overlap is with browser-chrome.

## 3.9 Gaps (both directions)

**Manual-only (little/no tree coverage) — must stay manual or move to this repo's Selenium suite:** real-world
site compatibility & media/WebRTC on live sites (526 cases); installer/uninstaller/OS packaging + NVDA installs
(366); visual/NOVA redesign & Figma compliance (≈800 across redesign + design subsets); antivirus interop (86),
Windows Recall (10), real DRM/Widevine (72), FxA live-account flows (26), language-pack update resilience;
Shopping/Review Checker (102 — feature removed, retire these cases).

**Tree-only (no manual counterpart, by design):** all xpcshell **unit** logic; **web-platform-tests** standards +
**reftests/crashtests** rendering/robustness; **GTest** native units; **Talos/Raptor/mozperftest** performance.

These confirm the suites are **complementary, not redundant** — the tree owns the sub-UI correctness pyramid; the
manual suite owns real-environment, cross-cutting, and visual UX validation. The 43% STRONG band is a candidate
list for deciding which manual cases could be *retired in favor of* (or converted into) existing in-tree
browser-chrome automation, and which should instead be automated in this repo's own Selenium/Marionette POM suite.

## 3.10 Key findings & caveats (Part 3)

1. **One tree suite carries almost all the overlap: browser-chrome (`browser_*.js`).** "Is this manual case
   already automated upstream?" → only if a matching `browser_*.js` exists.
2. **Overlap is 43% STRONG / 35% PARTIAL / 19% WEAK / 3% NONE.** Even STRONG is *core-mechanic* overlap; the
   manual suite's real-site/locale/OS/visual/restart dimensions remain uniquely manual.
3. **Path drift verified (July 2026 tree):** tabs moved to `browser/components/tabbrowser/` (old
   `browser/base/content/test/tabs/` 404s); New Tab/Activity Stream moved to `browser/extensions/newtab/`; DoH is
   under `toolkit/components/doh/`; EME has no `test/` under `dom/media/eme/` (tests in `dom/media/test/`).
4. **Removed feature:** Shopping / Review Checker is gone — 102 manual cases have no live counterpart.
5. **Smart tab grouping** manual cases likely map to `browser/components/tabbrowser/`, not `browser/components/genai/`.
6. **Counts are as-verified snapshots.** Manual counts are exact (parsed JSON); tree counts drift per release.

## 3.11 Appendix — full manual suite → feature-area index (103 suites, 10,736 cases)

`suite_id` = TestRail suite ID from `manual_tests/all_cases.json`. Names in quotes confirmed via this repo's
`tests/**/conftest.py`; others inferred from case titles.

| suite_id | Inferred name | Cases | Feature area | Overlap |
|---|---|---:|---|---|
| 65334 | "Address Bar 138+" | 1068 | Address Bar / URL bar | STRONG |
| 5403 | "Pocket New Tab" | 529 | New Tab / Pocket | PARTIAL |
| 2241 | "Preferences" | 527 | Settings / Preferences | STRONG |
| 43517 | "Password manager" | 427 | Passwords / Logins | STRONG |
| 3045 | Search engines via policy | 358 | Enterprise Policies / Search | PARTIAL |
| 5833 | "Security and Privacy" | 354 | Site Identity / Connection | STRONG |
| 69142 | Backup Restore Dialog | 297 | Backup & Restore | PARTIAL |
| 1731 | Media top sites / playback | 292 | Media / Site Compatibility | WEAK |
| 95385 | HNT customize / wallpapers | 288 | New Tab customization | PARTIAL |
| 70197 | Search urlbar/searchbar | 231 | Search flows | PARTIAL |
| 29219 | Downloads | 224 | Downloads | STRONG |
| 2054 | "Form Autofill" | 222 | Form Autofill | STRONG |
| 2525 | Bookmarks Toolbar | 222 | Bookmarks / Places | STRONG |
| 103322 | NOVA chrome design | 221 | UI / Visual redesign | WEAK |
| 69666 | Passwords & Autofill settings design | 205 | Settings (design) | WEAK |
| 65 | Find in page / PDF find | 196 | Find in page / PDF | STRONG |
| 73 | Nimbus Enroll/Rollout | 192 | Experiments / Nimbus | PARTIAL |
| 97961 | Backup restore dialog | 192 | Backup & Restore | PARTIAL |
| 97948 | Urlbar dropdown redesign | 181 | Address Bar UI | WEAK |
| 42945 | about:firefoxview | 180 | Firefox View | STRONG |
| 70279 | AI window / sidebar onboarding | 175 | GenAI | STRONG |
| 1940 | Backup/restore preferences | 167 | Backup & Restore | PARTIAL |
| 73807 | Backup restore dialog | 164 | Backup & Restore | PARTIAL |
| 1997 | "Theme and Toolbar" | 162 | Themes / Toolbar | PARTIAL |
| 2542 | DevTools inspector | 158 | DevTools | PARTIAL |
| 23035 | Easy Setup onboarding | 155 | Onboarding | STRONG |
| 1694 | Site compat glitches | 147 | Media / Site Compatibility | WEAK |
| 18105 | NVDA install accessibility | 145 | Accessibility / Installer | WEAK |
| 66659 | Text fragments | 114 | Text fragments | WEAK |
| 2103 | "Tabbed Browser" | 113 | Tabs | STRONG |
| 100373 | Smart Window Switcher NOVA | 112 | UI / Visual redesign | WEAK |
| 53810 | Sidebar | 105 | Sidebar | STRONG |
| 69469 | Firefox Enterprise client install | 103 | Enterprise / Installer | PARTIAL |
| 43337 | Shopping sidebar | 102 | Shopping / Review Checker | NONE |
| 102 | Scrolling | 94 | Scrolling / Rendering | WEAK |
| 1697 | WebRTC AV conferencing | 87 | WebRTC / Media | WEAK |
| 24370 | Antivirus compatibility | 86 | 3rd-party / AV compat | NONE |
| 100482 | Share Folder bookmarks | 86 | Bookmarks / Places | STRONG |
| 5252 | Windows installer | 85 | Installer | WEAK |
| 6066 | http/proxy/DNS | 82 | Network / Proxy / DoH | PARTIAL |
| 85 | Context menu | 77 | Context menu | PARTIAL |
| 59371 | Terms of Service onboarding | 75 | Onboarding / ToU | STRONG |
| 103289 | Onboarding | 75 | Onboarding | STRONG |
| 71226 | rpm package install | 72 | Installer (Linux) | WEAK |
| 68 | "Session Restore" | 67 | Session Restore | STRONG |
| 70336 | DRM / Widevine CDM | 65 | DRM / EME | WEAK |
| 71056 | Tab Notes | 60 | Tabs / Tab Notes | PARTIAL |
| 1907 | "Notifications, Push and Alerts" | 56 | Notifications | PARTIAL |
| 2119 | Profiles create/rename | 56 | Profiles | STRONG |
| 6874 | Disable autoupdate policy | 54 | Enterprise / Update | PARTIAL |
| 95392 | Threshold URL block | 49 | Content blocking | PARTIAL |
| 943 | Screenshots | 48 | Screenshots | STRONG |
| 2085 | "Find Toolbar" | 46 | Find in page | STRONG |
| 73695 | Default search engine dropdown | 45 | Search flows | PARTIAL |
| 97970 | Legacy profiles migration | 45 | Profiles / Migration | PARTIAL |
| 76324 | Privacy & Security page | 44 | Settings (design) | WEAK |
| 5259 | Drag/drop file hosting | 42 | Drag & Drop / File handling | PARTIAL |
| 71443 | Block GenAI features policy | 42 | GenAI / Enterprise | PARTIAL |
| 74 | IE data migration | 41 | Migration | PARTIAL |
| 71394 | Translate quick action urlbar | 40 | Translations | STRONG |
| 103666 | Keyboard shortcuts customization | 40 | Keyboard shortcuts | PARTIAL |
| 67503 | Lists / tasks | 39 | Misc / Lists | NONE |
| 70264 | Desktop shortcut toggle installer | 39 | Installer | WEAK |
| 95356 | Urlbar css redesign | 39 | Address Bar UI | WEAK |
| 100943 | Saved credentials autofill dropdown | 38 | Passwords / Logins | STRONG |
| 69070 | Local Network Access prompt | 37 | Permissions | STRONG |
| 1977 | PDF viewer pdf.js | 35 | PDF viewer | STRONG |
| 69749 | Home & Startup settings redesign | 34 | Settings (design) | WEAK |
| 70723 | Rename tabs | 30 | Tabs | STRONG |
| 69039 | Weather widget newtab | 28 | New Tab | PARTIAL |
| 60629 | about:studies experiments | 27 | Experiments / Nimbus | PARTIAL |
| 2130 | Firefox Account create/recovery | 26 | FxA / Sync | PARTIAL |
| 100742 | QR code generation | 26 | Address Bar / QR | PARTIAL |
| 103224 | DevTools horizontal tabs | 26 | DevTools | PARTIAL |
| 69569 | rust_migration telemetry | 23 | Migration / Telemetry | PARTIAL |
| 69048 | GPU process sandbox | 21 | Sandbox / GPU | WEAK |
| 2052 | Uninstaller | 20 | Installer | WEAK |
| 69570 | placeholder junk | 20 | Placeholder / Junk | NONE |
| 88 | Image formats | 18 | Image rendering / compat | WEAK |
| 5260 | Update language pack | 17 | Software Update | PARTIAL |
| 69083 | Top sites frecency sponsored | 17 | New Tab / Top sites | PARTIAL |
| 100547 | Private Window appearance | 17 | Private Browsing | STRONG |
| 90661 | Proxy settings | 16 | Network / Proxy / DoH | PARTIAL |
| 1998 | Title Bar / Toolbars customize | 15 | Toolbar customization | PARTIAL |
| 69060 | Feature opt-in EU | 15 | GenAI / opt-in | PARTIAL |
| 73783 | Reduced Protection PBM/ETP | 13 | ETP / Privacy | STRONG |
| 66264 | Screenshots / Recall | 10 | Privacy / Recall | NONE |
| 100772 | WebGL fingerprinting flags | 10 | Anti-fingerprinting / RFP | PARTIAL |
| 76427 | ToU onboarding Fedora | 9 | Onboarding / ToU | STRONG |
| 2126 | Reader View | 8 | Reader View | STRONG |
| 49853 | Gnome Extensions addon | 8 | Add-ons (Linux) | PARTIAL |
| 95476 | Backup restore OneDrive | 8 | Backup & Restore | PARTIAL |
| 68092 | DRM Widevine | 7 | DRM / EME | WEAK |
| 67 | Crash Reporter | 6 | Crash Reporter | WEAK |
| 498 | Geolocation share | 6 | Permissions / Geolocation | STRONG |
| 22801 | Language packs install | 6 | Localization | PARTIAL |
| 54271 | Feature access misc | 6 | Misc | NONE |
| 75504 | UI as designed misc | 6 | UI / misc | NONE |
| 187 | Branding builds | 5 | Branding | NONE |
| 71059 | rpm install | 5 | Installer (Linux) | WEAK |
| 100768 | Click Me demo | 5 | Placeholder / Junk | NONE |
| 100845 | Attention message demo | 5 | Placeholder / Junk | NONE |
| 5202 | Telemetry / Default Browser Agent | 3 | Telemetry / DBA | WEAK |

---
---

# Part 4 — Exact Firefox Tree Test Locations (verified path index)

> Parts 1–3 referenced many tests by directory or by filename fragment (e.g. `browser-autofill/browser_originToAdaptive.js`
> without its `browser/components/urlbar/tests/` prefix, or `tabs/browser_pinnedTabs.js` without its component root).
> This part gives the **complete, root-relative path** for every referenced test directory and example file, each
> **verified to exist on searchfox against current mozilla-central** (July 2026). It covers **both** comparisons:
> §4.2 = the automated STARfox comparison (Parts 1–2); §4.3 = the manual-suite comparison (Part 3).
>
> **All paths below are root-relative from the mozilla-central tree root.** To open any path in a browser, prefix it
> with `https://searchfox.org/mozilla-central/source/` (e.g.
> `https://searchfox.org/mozilla-central/source/browser/components/urlbar/tests/browser-autofill/browser_originToAdaptive.js`).
> The GitHub mirror equivalent is `https://github.com/mozilla-firefox/firefox/blob/main/<path>`.

## 4.0 Corrections applied during verification (read first)

While resolving paths, several references in Parts 1–2 were found to be inexact. Corrected here:

| As written in Parts 1–2 | Reality in current tree |
|---|---|
| tab tests under `browser/base/content/test/tabs/` | **Moved** — that path 404s; all tab tests are now under `browser/components/tabbrowser/test/browser/tabs/` |
| `browser_devices_get_user_media*` (WebRTC) implied camelCase | Actual files are snake_case: `browser_devices_get_user_media*.js` |
| `browser_permissions_*` (webextension perm prompts) | **No such prefix.** Real files use `browser_ext_*`: e.g. `browser_ext_request_permissions.js`, `browser_ext_popup_requestPermission.js` |
| printing tests under `browser/components/printing/tests` | **Wrong root** — printing tests are in `toolkit/components/printing/tests/` |
| page context-menu tests under `contextmenu/` | Directory is `browser/base/content/test/contextMenu/` (capital **M**) |
| `browser_fxa_web_channel.js` under `services/...` | Actually `browser/base/content/test/sync/browser_fxa_web_channel.js` |
| Megalist (sidebar passwords) under `aboutlogins/` | Actually `toolkit/components/satchel/megalist/content/tests/browser/` |
| `browser_search_glean_serp_event_telemetry` (bare) | Only one file matches, with a suffix: `browser_search_glean_serp_event_telemetry_categorization_enabled_by_pref.js` |
| `browser_sidebar_pinned_tabs.js` | **Not found**; closest existing is `browser_sidebar_pinned_tab_promo.js` |
| `browser_autoplay_blocked.js` | **Not found** by this name; autoplay tests are `dom/media/autoplay/test/browser/browser_autoplay_policy_*.js` |
| `browser_audioTabIcon.js` "gone" | **Exists** at `browser/components/tabbrowser/test/browser/tabs/browser_audioTabIcon.js` (it moved with the tab tests, not deleted) |

## 4.1 Master directory index (both comparisons share these tree roots)

Every feature area in this document maps to one or more of these **verified** test directories. Framework tags:
BC = browser-chrome (`browser_*.js`), XP = xpcshell unit, MN = marionette, MC = mochitest-chrome, MP = mochitest-plain.

| Feature area | Exact tree test directory | Framework |
|---|---|---|
| Address bar / urlbar | `browser/components/urlbar/tests/browser/`, `.../browser-autofill/`, `.../browser-searchMode/`, `.../browser-UrlbarInput/`, `.../browser-UrlbarView/`, `.../browser-tips/`, `.../browser-switchTab/`, `.../browser-quickactions/`, `.../browser-telemetry/`, `.../quicksuggest/browser/`, `.../unit/` | BC + XP |
| Search UI | `browser/components/search/test/browser/` (+ `telemetry/` subdir) | BC |
| Search service | `toolkit/components/search/tests/xpcshell/` | XP |
| Tabs / tab bar / groups | `browser/components/tabbrowser/test/browser/tabs/`, `.../dragdrop/`, `.../tabMediaIndicator/`, `.../smarttabgrouping/`, `.../statuspanel/` | BC |
| Session restore | `browser/components/sessionstore/test/` (+ `unit/`) | BC + XP |
| Toolbar / customize / theme | `browser/components/customizableui/test/` | BC |
| Firefox View | `browser/components/firefoxview/tests/browser/` (+ `tests/chrome/`) | BC + MC |
| Sidebar / vertical tabs | `browser/components/sidebar/tests/browser/`, `.../tests/marionette/`, `.../tests/unit/` | BC + MN + XP |
| Passwords (about:logins) | `browser/components/aboutlogins/tests/browser/` (+ `chrome/`, `unit/`) | BC + MC + XP |
| Password mgr (doorhanger/autofill) | `toolkit/components/passwordmgr/test/browser/` (+ `mochitest/`, `unit/`) | BC + MP + XP |
| Sidebar passwords (Megalist) | `toolkit/components/satchel/megalist/content/tests/browser/` | BC |
| Form autofill | `browser/extensions/formautofill/test/browser/` (+ `address/`, `creditCard/`, `heuristics/`, `fathom/`) | BC |
| Bookmarks / Places / Library | `browser/components/places/tests/browser/` (+ `interactions/`), `toolkit/components/places/tests/browser/` | BC |
| Downloads | `browser/components/downloads/test/browser/` (+ `unit/`) | BC + XP |
| Preferences / Settings | `browser/components/preferences/tests/` + pane subdirs (`privacy/`, `home/`, `search/`, `downloads/`, `applications/`, `languages/`, `siteData/`, `sync/`, `etp/`, `aiFeatures/`, …) | BC |
| Migration | `browser/components/migration/tests/browser/` (+ `unit/`) | BC + XP |
| Profiles | `browser/components/profiles/tests/browser/` (+ `unit/`), `toolkit/profile/test/` | BC + XP |
| Backup & Restore | `browser/components/backup/tests/browser/`, `.../chrome/`, `.../marionette/`, `.../xpcshell/` | BC + MC + MN + XP |
| New Tab / Activity Stream | `browser/extensions/newtab/test/browser/`, `.../unit/`, `.../xpcshell/` (+ Jest); `browser/components/newtab/test/browser/` | BC + XP + Jest |
| Top sites | `browser/components/topsites/test/` | BC + XP |
| Onboarding / about:welcome | `browser/components/aboutwelcome/tests/browser/` (+ `unit/`, `xpcshell/`) | BC + XP |
| Messaging (CFR/spotlight/callout) | `browser/components/asrouter/tests/browser/` (+ `unit/`, `xpcshell/`) | BC + XP |
| GenAI (chatbot/link preview) | `browser/components/genai/tests/browser/` (+ `chrome/`, `xpcshell/`); `browser/components/aiwindow/` | BC + MC + XP |
| Site identity / connection | `browser/base/content/test/siteIdentity/` | BC |
| ETP / protections panel | `browser/base/content/test/protectionsUI/` | BC |
| Anti-tracking behavior | `toolkit/components/antitracking/test/browser/` (+ `xpcshell/`, `marionette/`, `gtest/`) | BC + XP + MN + GTest |
| Anti-fingerprinting (RFP) | `toolkit/components/resistfingerprinting/tests/browser/`, `.../chrome/`, `.../xpcshell/`, `.../gtest/` | BC + XP + GTest |
| Private browsing | `browser/components/privatebrowsing/test/browser/` | BC |
| WebRTC device prompts | `browser/base/content/test/webrtc/` | BC |
| Permissions | `browser/base/content/test/permissions/` | BC |
| WebExtension perm prompts | `browser/components/extensions/test/browser/` | BC |
| Popup blocker | `browser/base/content/test/popups/` | BC |
| DoH | `toolkit/components/doh/test/browser/` | BC |
| Cookie banners | `toolkit/components/cookiebanners/test/browser/` | BC |
| Bounce tracking | `toolkit/components/bouncetrackingprotection/test/browser/` | BC |
| Translations | `browser/components/translations/tests/browser/` | BC |
| Reader View | `toolkit/components/reader/tests/browser/` (+ `chrome/`) | BC + MC |
| Screenshots | `browser/components/screenshots/tests/browser/` | BC |
| Find in page (findbar) | `toolkit/content/tests/browser/` (findbar files), `toolkit/content/tests/chrome/` | BC + MC |
| PDF viewer (pdf.js) | `toolkit/components/pdfjs/test/` (+ `unit/`) | BC + XP |
| Printing | `toolkit/components/printing/tests/` | BC |
| Zoom | `browser/base/content/test/zoom/` | BC |
| Page context menu | `browser/base/content/test/contextMenu/` | BC |
| Autoplay / media policy | `dom/media/autoplay/test/browser/`; `toolkit/content/tests/browser/browser_delay_autoplay_media.js` | BC + MP |
| EME / DRM (ClearKey) | `dom/media/test/` (`test_eme_*.html`) | MP |
| Text fragments | `dom/base/test/` (`test_text-fragments-*.html`) + WPT | MP + WPT |
| Enterprise policies | `browser/components/enterprisepolicies/tests/browser/` (+ `xpcshell/`) | BC + XP |
| Software update | `toolkit/mozapps/update/tests/browser/`, `.../marionette/`, `.../unit_aus_update/`, `.../unit_background_update/`, `.../gtest/` | BC + MN + XP + GTest |
| FxA web channel / sign-in | `browser/base/content/test/sync/` | BC |
| Sync engine | `services/sync/tests/` | XP |
| Crash reporter | `toolkit/crashreporter/test/` | XP + limited BC |
| Accessibility (a11y API) | `accessible/tests/mochitest/` (+ `browser/`) | MC/a11y + BC |
| Installer / packaging | `browser/installer/`, `toolkit/mozapps/installer/` | build/packaging |
| Firefox UI functional (E2E, restart) | `testing/firefox-ui/tests/functional/` | MN (firefox-ui) |
| Shopping / Review Checker | **removed from tree** (was `browser/components/shopping/`) | — |

## 4.2 Automated STARfox comparison (Parts 1–2) — exact file paths

Full verified paths for every example file referenced in Part 1, grouped by directory.

### Address bar & search (§1.1)

`browser/components/urlbar/tests/browser/`
- `browser_inputHistory_autofill.js`, `browser_remove_match.js`, `browser_inputHistory.js`, `browser_add_search_engine.js`,
  `browser_contextualsearch_install.js`, `browser_keyword.js`, `browser_tokenAlias.js`, `browser_action_searchengine_alias.js`,
  `browser_clipboard.js`, `browser_copying.js`, `browser_canonizeURL.js`, `browser_placeholder.js`, `browser_searchSettings.js`,
  `browser_top_sites.js`, `browser_urlbar_contextmenu.js`, `browser_pasteAndGo.js`, `browser_oneOffs.js`, `browser_tabToSearch.js`,
  `browser_searchSuggestions.js`, `browser_redirect_error.js`, `browser_tabMatchesInAwesomebar.js`

`browser/components/urlbar/tests/browser-autofill/`
- `browser_originToAdaptive.js`, `browser_canonize.js`, `browser_trimURLs.js`

`browser/components/urlbar/tests/browser-searchMode/`
- `browser_indicator.js`, `browser_no_results.js`, `browser_searchModeSwitcher_searchMode.js`, `browser_switchTabs.js`,
  `browser_engineRemoval.js`, `browser_searchModeSwitcher_basic.js`, `browser_alias_replacement.js`

`browser/components/urlbar/tests/browser-UrlbarInput/`
- `browser_searchTerms.js`, `browser_searchTerms_switch_tab.js`

`browser/components/urlbar/tests/browser-tips/` — `browser_updateRefresh.js`
`browser/components/urlbar/tests/quicksuggest/browser/` — `browser_quicksuggest_addons.js`, `browser_quicksuggest.js`

`browser/components/search/test/browser/`
- `browser_addSearchEngineFromForm.js`, `browser_searchbar_default.js`, `browser_private_search_perwindowpb.js`,
  `browser_searchbar_enter.js`, `browser_contentSearch.js`, `browser_contextmenu.js`

`browser/components/search/test/browser/telemetry/`
- `browser_search_telemetry_sources.js`, `browser_search_telemetry_adImpression_component.js`,
  `browser_search_telemetry_sources_ads_clicks.js`, `browser_search_telemetry_abandonment.js`,
  `browser_search_glean_serp_event_telemetry_categorization_enabled_by_pref.js`

> Duplicate-name cautions (correct urlbar/search copy chosen above): `browser_inputHistory.js` also exists in `browser-switchTab/`;
> `browser_trimURLs.js` also in `browser-UrlbarInput/`; `browser_placeholder.js` also in `browser-autofill/`; `browser_clipboard.js`
> also under `browser/base/` and `toolkit/`; `browser_contextmenu.js` has 4 copies tree-wide.

### Tabs / session / toolbar / theme (§1.2)

`browser/components/tabbrowser/test/browser/tabs/`
- `browser_addAdjacentNewTab.js`, `browser_new_tab_url.js`, `browser_tabkeynavigation.js`,
  `browser_contextmenu_openlink_after_tabnavigated.js`, `browser_openURI_background.js`, `browser_window_open_modifiers.js`,
  `browser_tabfocus.js`, `browser_tabswitch_select.js`, `browser_list_all_tabs_menu_items.js`, `browser_overflowScroll.js`,
  `browser_pinnedTabs.js`, `browser_multiselect_tabs_pin_unpin.js`, `browser_tabReorder.js`, `browser_pinnedTabs_closeByKeyboard.js`,
  `browser_close_tab_by_dblclick.js`, `browser_undo_close_tabs.js`, `browser_tab_label_during_reload.js`, `browser_audioTabIcon.js`,
  `browser_multiselect_tabs_mute_unmute.js`, `browser_removeTabsToTheEnd.js`, `browser_removeAllTabsBut.js`,
  `browser_multiselect_tabs_move.js`, `browser_tab_groups.js`, `browser_tab_group_menu.js`, `browser_tab_groups_tabContextMenu.js`,
  `browser_tab_preview.js`, `browser_tab_dragdrop.js`

`browser/components/tabbrowser/test/browser/tabMediaIndicator/` — `browser_mute.js`
`browser/components/tabbrowser/test/browser/dragdrop/` — `browser_drag_to_pin.js`

`browser/components/sessionstore/test/`
- `browser_undoCloseById.js`, `browser_restoreLastClosedTabOrWindowOrSession.js`, `browser_tab_groups_save_on_window_close.js`,
  `browser_tab_groups_restore_to_group.js`, `browser_restoreLastActionCorrectOrder.js`,
  `browser_closed_objects_changed_notifications_tabs.js`

`browser/components/customizableui/test/`
- `browser_history_recently_closed.js`, `browser_reload_tab.js`, `browser_switch_to_customize_mode.js`, `browser_customizemode_lwthemes.js`

`browser/components/firefoxview/tests/browser/` — `browser_recentlyclosed_firefoxview.js`
`browser/components/profiles/tests/browser/` — `browser_test_current_theme_from_amo.js`

### Security / privacy / networking / notifications / geo (§1.3)

`browser/base/content/test/protectionsUI/`
- `browser_protectionsUI.js`, `browser_protectionsUI_fingerprinters.js`, `browser_protectionsUI_cookie_banner.js`,
  `browser_protectionsUI_cryptominers.js`, `browser_protectionsUI_categories.js`

`browser/base/content/test/siteIdentity/`
- `browser_identityPopup_clearSiteData.js`, `browser_identity_UI.js`, `browser_check_identity_state.js`,
  `browser_mixed_passive_content_indicator.js`, `browser_csp_block_all_mixedcontent.js`, `browser_identityPopup_HttpsOnlyMode.js`,
  `browser_geolocation_indicator.js`

`browser/base/content/test/webrtc/` — `browser_devices_get_user_media.js`, `browser_devices_get_user_media_screen.js`, `browser_devices_get_user_media_in_frame.js`, `browser_devices_get_user_media_default_permissions.js`
`browser/base/content/test/permissions/` — `browser_permission_delegate_geo.js`
`browser/base/content/test/popups/` — `browser_popup_blocker.js`, `browser_popup_blocker_frames.js`, `browser_popup_blocker_identity_block.js`, `browser_popup_blocker_iframes.js`
`browser/components/privatebrowsing/test/browser/` — `browser_privatebrowsing_ui.js`, `browser_privatebrowsing_indicator.js`, `browser_privatebrowsing_permissions.js` (+ ~43 more)
`browser/components/extensions/test/browser/` — `browser_ext_request_permissions.js`, `browser_ext_popup_requestPermission.js`, `browser_ext_persistent_storage_permission_indication.js`
`toolkit/components/doh/test/browser/` — `browser_remoteSettings_rollout.js`, `browser_providerSteering.js`, `browser_throttle_heuristics.js`, `browser_trrSelect.js`
`toolkit/components/antitracking/test/browser/` — `browser_blockingCookies.js`, `browser_partitionedCookies.js`, `browser_hasStorageAccess.js`, `browser_urlQueryStringStripping.js`, `browser_contentBlockingTelemetry.js`

### Password manager & form autofill (§1.4)

`browser/components/aboutlogins/tests/browser/` — `browser_createLogin.js`, `browser_updateLogin.js`, `browser_deleteLogin.js`, `browser_copyToClipboardButton.js`, `browser_loginFilter.js`, `browser_openSite.js`, `browser_primaryPassword.js`, `browser_osAuthDialog.js`, `browser_openExport.js`
`toolkit/components/passwordmgr/test/browser/` — `browser_doorhanger_save_password.js`, `browser_exceptions_dialog.js`, `browser_autocomplete_insecure_warning.js`, `browser_openPasswordManager.js`, `browser_autocomplete_primary_password.js`, `browser_context_menu_generated_password.js`, `browser_doorhanger_generated_password.js`, `browser_preselect_login.js`, `browser_context_menu.js`, `browser_autofill_after_paint.js`
`toolkit/components/satchel/megalist/content/tests/browser/` — `browser_passwords_export_success_notification.js`
`browser/extensions/formautofill/test/browser/` — `browser_manageAddressesDialog.js`, `browser_clearPopulatedForm.js`, `browser_privacyPreferences.js`, `browser_submission_in_private_mode.js`
`browser/extensions/formautofill/test/browser/creditCard/` — `browser_manageCreditCardsDialog.js`, `browser_editCreditCardDialog.js`

### Bookmarks / history / downloads / preferences / profiles (§1.5)

`browser/components/places/tests/browser/` — `browser_bookmark_popup.js`, `browser_remove_bookmarks.js`, `browser_click_bookmarks_on_toolbar.js`, `browser_library_open_all.js`, `browser_bookmark_context_menu_contents.js`, `browser_autoshow_bookmarks_toolbar.js`, `browser_forgetthissite.js`
`browser/components/places/tests/browser/interactions/` — `browser_interactions_clearHistory.js`
`toolkit/components/places/tests/browser/` — `browser_visituri.js`
`browser/components/downloads/test/browser/` — `browser_basic_functionality.js`, `browser_downloads_context_menu_delete_file.js`, `browser_blocked_and_deleted_status.js`, `browser_downloads_panel_opens.js`
`browser/components/preferences/tests/` — `browser_advanced_update.js`; `downloads/browser_downloads.js`; `applications/browser_filetype_dialog.js`; `siteData/browser_clearSiteData_v2.js`; `privacy/browser_privacypane_3.js`; `home/browser_homepage_firefox_home.js`; `languages/browser_languages_pane.js`
`browser/components/migration/tests/browser/` — `browser_do_migration.js`, `browser_edge_bookmarks_success_strings.js`

### PDF / print / reader / find / media / zoom (§1.6)

`toolkit/components/pdfjs/test/` — `browser_pdfjs_main.js`, `browser_pdfjs_download_button.js`, `browser_pdfjs_navigation.js`, `browser_pdfjs_zoom.js`, `browser_pdfjs_form.js`, `browser_pdfjs_editing_contextmenu.js`, `browser_pdfjs_find.js`
`toolkit/components/printing/tests/` — `browser_modal_print.js`, `browser_preview_navigation.js`, `browser_print_stream.js`
`toolkit/components/reader/tests/browser/` — `browser_readerMode.js`, `browser_readerMode_textLayoutPref.js`, `browser_readerMode_colorSchemePref.js`
`toolkit/content/tests/browser/` — `browser_findbar.js`, `browser_findbar_marks.js`, `browser_delay_autoplay_media.js`
`browser/base/content/test/zoom/` — `browser_zoom_commands.js`, `browser_mousewheel_zoom.js`, `browser_default_zoom.js` (family: `_fission.js`, `_multitab.js`, `_sitespecific.js`)
> `browser_autoplay_blocked.js` as written does not exist — autoplay policy tests are `dom/media/autoplay/test/browser/browser_autoplay_policy_*.js`.

### Sidebar / AI / menus / sync (§1.7)

`browser/components/sidebar/tests/browser/` — `browser_toolbar_sidebar_button.js`, `browser_hide_sidebar.js`, `browser_vertical_tabs.js`, `browser_sidebar_expand_on_hover.js`, `browser_extensions_sidebar.js` (note: `browser_sidebar_pinned_tabs.js` not found; closest is `browser_sidebar_pinned_tab_promo.js`)
`browser/components/genai/tests/browser/` — `browser_chat_contextmenu.js`, `browser_chat_sidebar.js`, `browser_chat_page.js`, `browser_genai_init.js`
`browser/base/content/test/contextMenu/` — `browser_contextmenu.js`
`browser/base/content/test/sync/` — `browser_fxa_web_channel.js`

## 4.3 Manual-suite comparison (Part 3) — exact directories per feature area

The manual suite maps to whole tree test directories (not individual files). These are the exact, verified roots for the
STRONG/PARTIAL manual areas from §3.4–§3.5 (files inside them are illustrative — see §3.4 for verified examples):

| Manual feature area (§3.3) | Exact tree test directory(ies) |
|---|---|
| Passwords / Logins | `browser/components/aboutlogins/tests/browser/` + `toolkit/components/passwordmgr/test/browser/` (+ Megalist `toolkit/components/satchel/megalist/content/tests/browser/`) |
| Settings / Preferences | `browser/components/preferences/tests/` + pane subdirs (`privacy/`, `home/`, `search/`, `downloads/`, `applications/`, `languages/`, `siteData/`, `sync/`, `etp/`, `aiFeatures/`) |
| Bookmarks / Places | `browser/components/places/tests/browser/` (+ `interactions/`); `toolkit/components/places/tests/browser/` |
| Downloads | `browser/components/downloads/test/browser/` |
| Form Autofill | `browser/extensions/formautofill/test/browser/` (+ `address/`, `creditCard/`) |
| Tabs (+ Tab Notes) | `browser/components/tabbrowser/test/browser/tabs/` (+ `dragdrop/`, `tabMediaIndicator/`) |
| Firefox View | `browser/components/firefoxview/tests/browser/` |
| Sidebar | `browser/components/sidebar/tests/browser/` (+ `tests/marionette/`) |
| Screenshots | `browser/components/screenshots/tests/browser/` |
| Reader View | `toolkit/components/reader/tests/browser/` |
| Site Identity / Connection | `browser/base/content/test/siteIdentity/` |
| ETP / Privacy | `browser/base/content/test/protectionsUI/` |
| Onboarding (+ ToU) | `browser/components/aboutwelcome/tests/browser/` + `browser/components/asrouter/tests/browser/` |
| Find in page / PDF | `toolkit/content/tests/browser/` (findbar) + `toolkit/components/pdfjs/test/` |
| Translations | `browser/components/translations/tests/browser/` |
| Session Restore | `browser/components/sessionstore/test/` |
| Profiles | `browser/components/profiles/tests/browser/` + `toolkit/profile/test/` |
| Private Browsing | `browser/components/privatebrowsing/test/browser/` |
| GenAI | `browser/components/genai/tests/browser/` (+ `browser/components/aiwindow/`) |
| Permissions (+ geo) | `browser/base/content/test/permissions/` + `.../siteIdentity/browser_geolocation_indicator.js` |
| Address Bar / URL bar | `browser/components/urlbar/tests/browser*/` (see §4.1 for full subdir list) |
| Backup & Restore | `browser/components/backup/tests/browser/` (+ `chrome/`, `marionette/`, `xpcshell/`) |
| New Tab / Pocket / customization | `browser/extensions/newtab/test/browser/` (+ Jest `test/unit`); `browser/components/newtab/test/browser/`; `browser/components/topsites/test/` |
| Search flows | `browser/components/search/test/browser/` + `toolkit/components/search/tests/xpcshell/` |
| Enterprise Policies | `browser/components/enterprisepolicies/tests/browser/` (+ `xpcshell/`) |
| DevTools | `devtools/client/**/test/` (per-tool `test/browser/` and `test/` dirs) |
| Experiments / Nimbus | `toolkit/components/nimbus/test/` + `browser/components/asrouter/tests/` |
| Network / Proxy / DoH | `toolkit/components/doh/test/browser/` + `netwerk/**/test/` |
| Content blocking | `toolkit/components/antitracking/test/browser/` |
| Anti-fingerprinting / RFP | `toolkit/components/resistfingerprinting/tests/{browser,chrome,xpcshell,gtest}/` |
| Themes / Toolbar | `browser/themes/**` + `browser/components/customizableui/test/` |
| Migration | `browser/components/migration/tests/{browser,unit}/` |
| FxA / Sync | `browser/base/content/test/sync/` (web channel) + `services/sync/tests/` |
| Software Update | `toolkit/mozapps/update/tests/{browser,marionette,unit_aus_update,unit_background_update}/` + `testing/firefox-ui/tests/functional/` |
| Notifications | `toolkit/components/**` (alerts/notifications) + web-notification mochitests |
| Context menu | `browser/base/content/test/contextMenu/` (+ per-feature `*context_menu*.js`) |
| Drag & Drop / File handling | `browser/components/tabbrowser/test/browser/dragdrop/` + file-handler tests |
| Media / Site Compatibility | `dom/media/test/` (mochitest); no site-compat analog |
| DRM / EME | `dom/media/test/` (`test_eme_*.html`, ClearKey) |
| Text fragments | `dom/base/test/` (`test_text-fragments-*.html`) + `testing/web-platform/tests/` |
| Accessibility / NVDA | `accessible/tests/mochitest/` (a11y API only; no NVDA analog) |
| Installer / Uninstaller | `browser/installer/`, `toolkit/mozapps/installer/` (packaging; largely no test analog) |
| Crash Reporter | `toolkit/crashreporter/test/` |
| Shopping / Review Checker | **removed** — no directory in current tree |



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
   manual cases. This caught real errors - see section 5.4.
5. **Every cited path was then machine-validated** against the tree inventory
   (`manual_tests/analysis/validate_paths.py`): **1,441 distinct citations, all resolving to a real
   file or directory**. Five wrong filenames were caught and corrected this way (the affected
   verdicts did not change - each of those clusters cites several other verified tests).

## 5.2 Results by suite

| Suite | TestRail suite | Cases | STRONG (de-prioritise) | % | Reviewed-but-kept |
|---|---|---:|---:|---:|---:|
| 65334 | Address Bar 138+ | 1068 | **787** | 74% | 202 |
| 2241 | Preferences | 527 | **325** | 62% | 201 |
| 2525 | Bookmarks Toolbar (+ History/Library) | 222 | **211** | 95% | 10 |
| 43517 | Password manager | 427 | **200** | 47% | 66 |
| 5833 | Security and Privacy | 354 | **187** | 53% | 34 |
| 2054 | Form Autofill | 222 | **180** | 81% | 42 |
| 29219 | Downloads | 224 | **153** | 68% | 58 |
| 70279 | AI window / Smart Window | 175 | **115** | 66% | 60 |
| 23035 | Easy Setup onboarding | 155 | **83** | 54% | 10 |
| 42945 | about:firefoxview | 180 | **82** | 46% | 73 |
| 103289 | Onboarding (Smart Window, 2nd suite) | 75 | **75** | 100% | 0 |
| 2103 | Tabbed Browser | 113 | **64** | 57% | 34 |
| 53810 | Sidebar | 105 | **36** | 34% | 47 |
| 68 | Session Restore | 67 | **30** | 45% | 15 |
| 943 | Screenshots | 48 | **26** | 54% | 4 |
| 100943 | Saved credentials autofill dropdown | 38 | **23** | 61% | 15 |
| 2085 | Find Toolbar | 46 | **17** | 37% | 9 |
| 71394 | Translate quick action / about:translations | 40 | **17** | 42% | 14 |
| 100482 | Share Folder / Curated Link Sharing | 86 | **14** | 16% | 15 |
| 2119 | Profiles | 56 | **14** | 25% | 12 |
| 69070 | Local Network / Device Access | 37 | **14** | 38% | 6 |
| 65 | Find in page / PDF viewer | 196 | **8** | 4% | 25 |
| 73783 | Reduced Protection (PBM/ETP) | 13 | **7** | 54% | 3 |
| 70723 | Rename tabs (Tab Notes) | 30 | **6** | 20% | 4 |
| 59371 | Terms of Service onboarding | 75 | **6** | 8% | 15 |
| 2126 | Reader View | 8 | **4** | 50% | 3 |
| 498 | Geolocation | 6 | **2** | 33% | 1 |
| 76427 | ToU onboarding on Linux distros | 9 | **0** | 0% | 9 |
| 100547 | Private Window appearance (NOVA) | 17 | **0** | 0% | 7 |
| | **Total (29 suites reviewed)** | **4619** | **2686** | **58%** | **994** |

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

---

# Part 6 - Critical, not-yet-automated manual cases with STRONG in-tree coverage

Round 4. Where Part 5 swept the whole manual corpus at every priority, this round answers a
narrower and more actionable question:

> Of the manual cases that are **Priority = Critical** and whose **Automation status is not
> Completed**, which ones are already covered by an automated test inside
> [mozilla-firefox/firefox](https://github.com/mozilla-firefox/firefox)?

Those are the cases most likely to be scheduled for manual execution *and* queued for STARfox
automation - so a duplicate here costs twice.

**Deliverable:** `manual_tests/CRITICAL_NOT_AUTOMATED_STRONG.csv`, plus
`manual_tests/analysis/crit_strong_case_numbers.md` for the bare TestRail case numbers grouped by
suite. Cases are named the way TestRail names them - `C` followed by the case id, e.g. **C3163606**.

## 6.1 Population

Selected from `manual_tests/all_cases.json` on `priority_id == 4` (Critical) and
`custom_automation_status != 4` (anything other than Completed):

| | Cases |
|---|---:|
| Unique cases in the export | 10,727 |
| Priority = Critical | 1,870 |
| ... of which Automation status is not Completed | **1,551** |
| Spread over | 57 suites |

Their current automation status:

| Automation status | Cases |
|---|---:|
| Suitable for automation | 846 |
| Untriaged | 388 |
| In progress | 313 |
| Not suitable | 4 |

## 6.2 Result

**737 of the 1,551 (48%) have a STRONG in-tree counterpart.** The remaining 814 were reviewed and
kept.

Every one of the 1,551 carries an explicit verdict - unlike Part 5, which recorded only the
positives - so the "kept" column here is a reviewed decision rather than an absence of review.

The 737 break down by their TestRail automation status as follows, and this is the headline:

| Automation status of the STRONG cases | Cases | What it means |
|---|---:|---|
| Suitable for automation | 287 | Queued for STARfox work the tree already does |
| **In progress** | **211** | **Being automated right now, in parallel with an existing in-tree test** |
| Untriaged | 238 | Not yet triaged; the triage can be skipped |
| Not suitable | 1 | - |

The 211 in-progress cases are the most immediately useful output: automation effort currently being
spent duplicating `mozilla-firefox/firefox`. They concentrate in Easy Setup onboarding (32),
Preferences (29), Security and Privacy (17), Tabbed Browser (15), Bookmarks Toolbar (14), Form
Autofill (13), Context menus (12) and about:firefoxview (11).

## 6.3 Results by suite

| Suite | TestRail suite | Critical & not automated | STRONG overlap | % | Reviewed-but-kept |
|---|---|---:|---:|---:|---:|
| 23035 | Easy Setup onboarding | 155 | **121** | 78% | 34 |
| 65334 | Address Bar 138+ | 74 | **53** | 72% | 21 |
| 2241 | Preferences | 47 | **46** | 98% | 1 |
| 69142 | Backup and Restore | 67 | **40** | 60% | 27 |
| 97961 | Backup and Restore (3rd suite) | 48 | **29** | 60% | 19 |
| 73807 | Backup and Restore (2nd suite) | 47 | **27** | 57% | 20 |
| 74 | Migration from other browsers | 32 | **26** | 81% | 6 |
| 1940 | OS integration (taskbar, default browser, shell) | 53 | **25** | 47% | 28 |
| 42945 | about:firefoxview | 37 | **22** | 59% | 15 |
| 5833 | Security and Privacy | 75 | **21** | 28% | 54 |
| 1731 | Media playback | 48 | **20** | 42% | 28 |
| 68 | Session Restore | 39 | **19** | 49% | 20 |
| 73 | Printing | 36 | **19** | 53% | 17 |
| 43517 | Password manager | 29 | **18** | 62% | 11 |
| 2103 | Tabbed Browser | 34 | **17** | 50% | 17 |
| 65 | Find in page / PDF viewer | 94 | **17** | 18% | 77 |
| 2119 | Profiles | 41 | **17** | 41% | 24 |
| 85 | Context menus | 29 | **16** | 55% | 13 |
| 2525 | Bookmarks Toolbar (+ History/Library) | 17 | **16** | 94% | 1 |
| 67503 | New Tab Lists widget | 16 | **14** | 88% | 2 |
| 2054 | Form Autofill | 15 | **13** | 87% | 2 |
| 29219 | Downloads | 21 | **12** | 57% | 9 |
| 95385 | New Tab widgets (timer, checklist) | 13 | **11** | 85% | 2 |
| 5403 | New Tab page and preferences | 26 | **11** | 42% | 15 |
| 943 | Screenshots | 15 | **11** | 73% | 4 |
| 71226 | Release smoke / regression matrix | 48 | **11** | 23% | 37 |
| 53810 | Sidebar | 24 | **9** | 38% | 15 |
| 69749 | about:settings#home | 9 | **9** | 100% | 0 |
| 1997 | Themes and appearance | 16 | **8** | 50% | 8 |
| 88 | Image formats | 9 | **7** | 78% | 2 |
| 102 | Scrolling and zoom | 34 | **7** | 21% | 27 |
| 103666 | about:keyboard shortcut customization | 7 | **7** | 100% | 0 |
| 2085 | Find Toolbar | 8 | **6** | 75% | 2 |
| 6066 | DNS over HTTPS / enterprise policies | 14 | **6** | 43% | 8 |
| 1907 | WebRTC camera / microphone / screen sharing | 7 | **6** | 86% | 1 |
| 66659 | Copy Link to Highlight (text fragments) | 7 | **5** | 71% | 2 |
| 5260 | Background Update Agent | 8 | **4** | 50% | 4 |
| 2542 | DevTools eager evaluation (DevEd) | 4 | **3** | 75% | 1 |
| 54271 | Translate selection panel | 6 | **3** | 50% | 3 |
| 70723 | Rename tabs (Tab Notes) | 7 | **2** | 29% | 5 |
| 2126 | Reader View | 3 | **2** | 67% | 1 |
| 498 | Geolocation | 2 | **1** | 50% | 1 |
| 5252 | Installers (Windows / Mac / Linux) | 47 | **0** | 0% | 47 |
| 2052 | Uninstall and Refresh Firefox | 10 | **0** | 0% | 10 |
| 5259 | Drag and drop / clipboard | 11 | **0** | 0% | 11 |
| 22801 | Language pack updates | 4 | **0** | 0% | 4 |
| 1694 | Top sites / real-world web compat | 55 | **0** | 0% | 55 |
| 1697 | Web compat / screen sharing overlay | 2 | **0** | 0% | 2 |
| 24370 | Third-party software interop | 13 | **0** | 0% | 13 |
| 69048 | Graphics rendering (WebRender) | 10 | **0** | 0% | 10 |
| 1977 | Graphics and hardware acceleration | 16 | **0** | 0% | 16 |
| 18105 | Accessibility (screen readers) | 27 | **0** | 0% | 27 |
| 49853 | Third-party add-ons interop | 7 | **0** | 0% | 7 |
| 67 | Crash reporter | 5 | **0** | 0% | 5 |
| 1998 | Full screen | 6 | **0** | 0% | 6 |
| 2130 | Firefox Accounts and Sync | 14 | **0** | 0% | 14 |
| 5202 | Default Browser Agent (Windows) | 3 | **0** | 0% | 3 |
| | **Total (57 suites)** | **1551** | **737** | **48%** | **814** |

## 6.4 Where the overlap is strongest

- **Easy Setup onboarding (121 of 155)** - `browser/components/aboutwelcome/tests/browser/` tracks
  this feature slide for slide: a test per screen (language switcher, mobile downloads, add-ons
  picker, gratitude, import, theme picker) plus `browser_aboutwelcome_glean.js` and
  `browser_aboutwelcome_impression_action.js` for the impression and click pings. The suite is 155
  critical cases but only 47 distinct flows - it restates the same slides per platform and entry
  point. The consistent exception is the "UI - Light Theme" rows, which enumerate layout, imagery
  and exact copy; those stay manual.
- **Backup and Restore (96 of 162 across suites 69142 / 73807 / 97961)** - the load-bearing test is
  `browser/components/backup/tests/marionette/test_backup.py`, which creates a real backup, recovers
  it into a fresh profile, then asserts resource by resource that cookies, logins, certificates,
  addresses, payment methods, form history, bookmarks, history, preferences, permissions,
  sessionstore and the newtab wallpaper survived. That single test subsumes most of the
  "verify &lt;data category&gt; is properly restored" matrix. `browser_settings_*.js` covers the
  about:settings pane, encryption, the about:welcome restore screen and the enterprise policies.
- **Profile migration (26 of 32)** - `browser/components/migration/tests/` has a per-source xpcshell
  test for every data type across Chrome, Chromium, Edge, Safari and 360se, plus browser-chrome
  tests for the wizard and its entry points. `test_MigrationUtils_timedRetry.js` even covers reading
  a source database locked by a *running* source browser, which is the variable half of this suite's
  matrix.
- **about:settings#home (9 of 9)** - `browser/components/preferences/tests/home/` carries 48 tests
  and matches this suite essentially one-for-one.
- **about:keyboard (7 of 7)** - `browser/components/customkeys/tests/browser/browser_CustomKeys.js`
  covers change / clear / clear-all / reset / reset-all, and `browser_aboutKeyboard.js` asserts the
  Glean metrics the five telemetry rows check.
- **New Tab widgets (25 of 29 across 67503 / 95385)** - the Lists and Focus Timer React components
  have thorough jsx unit tests that drive the real interactions and assert the dispatched actions.

## 6.5 Suites where nothing carried over

Fourteen suites returned zero STRONG cases. Each has one reason, and none of them is "nobody
looked":

- **Runs outside the browser** - Installers (47), Uninstall and Refresh (10), Default Browser Agent
  (3), Language pack updates (4). Stub and full installer UI, UAC elevation, MSIX, .dmg / .pkg, code
  signing, the uninstaller and the Task Scheduler agent have no test harness in the tree.
- **Needs the live web** - Top sites / real-world web compat (55), web compat / sharing overlay (2).
  The tree does not test against live sites, by design.
- **Needs third-party software** - Third-party software interop (13), third-party add-ons interop
  (7). Antivirus products, GNOME Shell extensions, KeePassXC.
- **Needs a real screen reader** - Accessibility (27). Every row drives NVDA, VoiceOver or ORCA.
  `accessible/tests/` is a large corpus but queries the a11y tree through the API; it does not run a
  screen reader, which is the thing under test.
- **Visual rendering judgement** - Graphics and hardware acceleration (16), WebRender (10), Full
  screen (6). "No rendering artifacts on popular sites" and window-decoration checks; the reftest
  corpus compares synthetic references, which is a different question.
- **Crosses the application boundary** - Drag and drop / clipboard (11). Dragging out to File
  Explorer or Preview, pasting into desktop applications, copying tables out of other browsers.
- **Needs live credentials and a second device** - Firefox Accounts and Sync (14).
- **Needs a real crash and a live endpoint** - Crash reporter (5).

## 6.6 Suite labels corrected

Five suites were misnamed in the working notes and are fixed in
`manual_tests/analysis/crit_pop.py`. Worth knowing if you filter TestRail by these ids:

| Suite | Was assumed | Actually |
|---|---|---|
| 71226 | Session Restore (2nd suite) | Release smoke / regression matrix - live sites, themes, printing, PDF, scrolling, crash reports, Sync |
| 54271 | Picture-in-Picture | Translate selection panel |
| 2542 | Search engines | DevTools eager ("instant") evaluation, DevEdition |
| 5202 | Keyboard shortcuts | Default Browser Agent, Windows |
| 22801 | Notifications | Language pack updates |

## 6.7 Method

Same tiering as Part 5, run against a **freshly rebuilt tree inventory**:

- `manual_tests/analysis/fetch_tree.py` rebuilds `.fxtree/` from the GitHub git-trees API. This
  round is against `main` @ `5069177` (2026-08-12), where Part 5 was against `7d438b9` (2026-07-30).
  The `gfx` and `layout` subtrees were added to the inventory during this round.
- `c_01_*.py` ... `c_11_*.py` hold the verdicts as data, same shape as the `d_*.py` ledger.
  `c_util.py` adds `CT()` (cluster by case title) and `CREST()` (cluster the suite remainder) for the
  repetition-matrix suites, where listing ids by hand invites transcription errors.
- `c_10_prior_rounds.py` replays the verdicts rounds 1-3 already reached for the 482 population
  cases they had assessed, rather than re-deriving them and risking a needless disagreement with the
  published `LOW_PRIORITY_CANDIDATES.csv`. Where this round examined a suite in more detail, this
  round's verdict wins.
- `build_crit_report.py` writes the CSV, the summary table and the case-number listing. It fails
  loudly on a case claimed by two clusters or on an id outside the population; both are currently
  zero.
- `validate_crit_paths.py` checks every tree path cited in the ledger against the inventory.
  **1,084 distinct cited paths, 0 unverified.**

## 6.8 Caveats

- Point-in-time snapshot of `main` @ `5069177` (2026-08-12). Re-run `fetch_tree.py`,
  `validate_crit_paths.py` and `build_crit_report.py` before acting on this in a later cycle.
- "STRONG" means *the same user flow is asserted somewhere in the tree*, not that the assertions are
  identical. A manual case can still catch a regression its in-tree counterpart misses.
- pdf.js is the one place where "not in the tree" is misleading: the page-organize, merge, signature,
  image and alt-text editors are tested upstream in mozilla/pdf.js.
  `toolkit/components/pdfjs/test/` only covers the integration layer, so those rows are kept here.
  If the comparison is widened to include upstream pdf.js, suite 65 would move substantially.
- De-prioritising is not deleting, and this is a stronger claim than Part 5's, because these are
  Critical cases. The recommendation is to **stop queueing them for STARfox automation** and to skip
  them during crunch - not to retire them.
