# Round-5 housekeeping findings

## TestRail points at STARfox tests that no longer exist (7)

`custom_automated_test_names` names a file that is not in the repo. Either the test was renamed and TestRail was not updated, or it was deleted while the case stayed marked as automated.

| Cited path | Cases |
|---|---|
| `l10n_CM/Unified/test_demo_ad_name_org_captured_in_doorhanger_and_stored.py` | C2888701 |
| `tests/address_bar_and_search/test_seach_suggestions_can_be_disabled.py` | C3028773 |
| `tests/bookmarks_and_history/test_opened_website_in_new_tab_present_in_toolbar_history.py` | C118802 |
| `tests/bookmarks_and_history/test_opened_website_in_new_window_present_in_toolbar_history.py` | C118805 |
| `tests/bookmarks_and_history/test_opened_website_present_in_toolbar_history.py` | C118800 |
| `tests/downloads/test_download_apk_and_check_extesion.py` | C1836830 |
| `tests/sidebar/test_sidebar-button-always-displayed-on-a-fresh-profile.py` | C2639191 |

## Cases marked as STARfox-covered with no usable test name (84)

| Case | Title |
|---|---|
| C118800 | Verify that the recently opened website is displayed in the Hamburger History submenu |
| C118802 | Verify that the website opened in a new tab is displayed in the Hamburger History submenu |
| C118805 | Verify that opened websites in a New Window are displayed in the Toolbar History submenu |
| C122352 | Form Autofill Create New Profile Address (Door-hanger) |
| C134640 | Verify that previously closed tabs can be reopened by using keyboard combination |
| C134654 | Verify that navigation through multiple tabs is allowed |
| C246978 | Verify that Pin/Unpin selected tabs works properly |
| C246989 | Verify that multi-selected tabs can be moved via context menu |
| C1018757 | Verify that zoom works on radio buttons |
| C1090684 | Verify the print preview page number indicator is working successfully |
| C1836830 | Verify that Firefox shows the file extension when downloading Android APK files |
| C1938259 | Verify that the drawing areas can be deleted, moved or resized |
| C2197845 | Verify that the keyboard shortcut restores multiple closed tabs |
| C2241080 | Verify the direct navigation to about:logins |
| C2241084 | Verify the navigation to about:logins from about:protections |
| C2639191 | Verify that the Sidebar button is always displayed with a fresh profile |
| C2746167 | Verify that Default Search Code: Google - US is correctly displayed and functional |
| C2793046 | Verify adding Tab Groups from tab context menu |
| C2796550 | Verify ungrouping tabs |
| C2863570 | SAP Search engine adclick - URL bar |
| C2863571 | SAP Search engine adclick - searchbar |
| C2863572 | SAP Search engine adclick - urlbar_handoff |
| C2863573 | SAP Search engine adclick - context menu |
| C2863574 | SAP Search engine adclick - unknown |
| C2863575 | SAP Search engine adclick - reload |
| C2863576 | SAP Search engine adclick - tabhistory |
| C2863577 | Search engine - withads URL bar |
| C2863578 | Search engine - withads searchbar |
| C2863579 | Search engine - withads urlbar_handoff |
| C2863580 | Search engine - withads context menu |
| C2863581 | Search engine - withads unknown SAP |
| C2863582 | Search engine - withads reload SAP |
| C2863583 | Search engine - withads tabhistory SAP |
| C2863584 | Verify if the langugage packs can be successfully installed from AMO and Firefox is correctly locali |
| C2863585 | Verify if the langugage packs can be successfully installed from "about:preferences" and Firefox is  |
| C2863590 | Experiment displayed in "about:studies" |
| C2863591 | Experiment displayed in "about:support" |
| C2863592 | Browser update to the following Fx version |
| C2863593 | Unenroll - Remove from "about:studies" |
| C2863594 | Unenroll - Opt-out from all studies |
| C2863625 | Navigate to a website using the Address bar |
| C2863626 | Navigate to a website using the "Paste and Go" option in the address bar |
| C2886580 | Verify that a new Address can be added |
| C2886581 | Verify the Capture Doorhanger is displayed after entering valid Address data |
| C2888557 | Verify Autofill Preview on hover over dropdown entries for name/org fields |
| C2888558 | Verify Autofill functionality when selecting an entry from the dropdown for name/org fields |
| C2888559 | Verify the yellow highlight appears on name/org fields |
| C2888560 | Verify clear functionality after selecting an entry from name/org fields |
| C2888561 | Verify Autofill Dropdown is displayed for address fields |
| C2888562 | Verify Autofill Preview on hover over dropdown entries for address fields |
| C2888563 | Verify Autofill functionality when selecting an entry from the dropdown for address fields |
| C2888564 | Verify the yellow highlight appears on address fields |
| C2888565 | Verify clear functionality after selecting an entry from address fields |
| C2888567 | Verify Autofill Dropdown is displayed for phone/email fields |
| C2888568 | Verify Autofill Preview on hover over dropdown entries for phone/email fields |
| C2888569 | Verify Autofill functionality when selecting an entry from the dropdown for phone/email fields |
| C2888570 | Verify the yellow highlight appears on phone/email fields |
| C2888571 | Verify clear functionality after selecting an entry from phone/email fields |
| C2888701 | Verify name/org fields are captured in the Capture Doorhanger and stored in about:preferences |
| C2888703 | Verify Address data are captured in the Capture Doorhanger and stored in about:preferences |
| C2888704 | Verify phone/email data are captured in the Capture Doorhanger and stored in about:preferences |
| C3028773 | Verify that search suggestions can be disabled |
| C3056980 | Verify that a new Credit Card can be added as Payment Method |
| C3056981 | Verify the Capture Doorhanger is displayed after entering valid Credit Card data |
| C3056982 | Verify Credit Card data is captured in the Capture Doorhanger and stored in about:preferences |
| C3056983 | Verify Autofill Dropdown is displayed for eligible fields |
| C3056984 | Verify Autofill Preview on hover over dropdown entries |
| C3056985 | Verify Autofill functionality when selecting an entry from the dropdown |
| C3056986 | Verify the yellow highlight appears on autofilled fields |
| C3056987 | Verify clear functionality after selecting an entry from the dropdown |
| C3186651 | Verify that multiple addresses can be added |
| C3186655 | Verify that multiple credit cards can be added |
| C3233962 | Verify that multiple credit cards can be added |
| C3233967 | Verify that multiple addresses can be added |
| C3248884 | Verify that Default Search Code: Google - US is correctly displayed and functional |
| C3255435 | Google US unknown |
| C3255449 | Bing tabhistory |
| C3255450 | Bing unknown |
| C3255464 | Duckduckgo tabhistory |
| C3255465 | Duckduckgo unknown |
| C3255479 | Ecosia tabhistory |
| C3255480 | Ecosia unknown |
| C3255494 | Qwant tabhistory |
| C3255495 | Qwant unknown |

## STARfox tests no TestRail case points at (46)

Not necessarily a problem -- some are meta/harness tests -- but any real feature test here is running in CI without a TestRail case recording that fact.

- `tests/address_bar_and_search/test_adaptive_history_autofill.py`
- `tests/address_bar_and_search/test_addon_suggestion.py`
- `tests/address_bar_and_search/test_default_search_provider_change_legacy_search_bar.py`
- `tests/address_bar_and_search/test_search_code_google_non_us.py`
- `tests/address_bar_and_search/test_search_code_google_us.py`
- `tests/address_bar_and_search/test_search_modes_for_sites.py`
- `tests/address_bar_and_search/test_search_suggestions.py`
- `tests/address_bar_and_search/test_search_suggestions_can_be_disabled.py`
- `tests/address_bar_and_search/test_search_term_persists.py`
- `tests/address_bar_and_search/test_server_not_found_error.py`
- `tests/address_bar_and_search/test_suggestion_engine_selection.py`
- `tests/address_bar_and_search/test_tile_menu_options.py`
- `tests/ai_controls/test_c3308998_unblock_restores_state.py`
- `tests/bookmarks_and_history/test_opened_website_in_new_tab_present_in_hamburger_history_menu.py`
- `tests/bookmarks_and_history/test_opened_website_in_new_window_present_in_hamburger_history_menu.py`
- `tests/bookmarks_and_history/test_opened_website_present_in_hamburger_history_menu.py`
- `tests/downloads/test_download_apk_and_check_extension.py`
- `tests/glean/serp_engagement/test_serp_engagement.py`
- `tests/meta/test_selectors.py`
- `tests/meta/test_version.py`
- `tests/password_manager/test_about_logins_direct_navigation.py`
- `tests/password_manager/test_about_logins_navigation_from_about_protections.py`
- `tests/password_manager/test_taobao_password_management.py`
- `tests/pdf_viewer/test_pdf_contextual_menu_actions.py`
- `tests/pdf_viewer/test_pdf_drawing_area_actions.py`
- `tests/pdf_viewer/test_pdf_zoom_radio_buttons.py`
- `tests/pocket/test_basic_de.py`
- `tests/pocket/test_basic_fr.py`
- `tests/pocket/test_basic_gb.py`
- `tests/pocket/test_basic_us.py`
- `tests/printing_ui/test_page_number_indicator_print_preview.py`
- `tests/security_and_privacy/test_blocking_cryptominers.py`
- `tests/security_and_privacy/test_blocking_fingerprinters.py`
- `tests/security_and_privacy/test_blocking_social_media_trackers.py`
- `tests/security_and_privacy/test_cross_site_tracking_cookies_blocked.py`
- `tests/security_and_privacy/test_detected_blocked_trackers_found.py`
- `tests/session_restore/test_restore_multiple_closed_tabs_at_once.py`
- `tests/sidebar/test_sidebar_button_always_displayed_on_fresh_profile.py`
- `tests/sync_and_fxa/test_existing_fxa.py`
- `tests/sync_and_fxa/test_new_fxa.py`
- `tests/tabs/test_group_tabs.py`
- `tests/tabs/test_move_multi_selected_tabs.py`
- `tests/tabs/test_navigation_multiple_tabs.py`
- `tests/tabs/test_pin_unpin_selected_tabs.py`
- `tests/tabs/test_reopen_tabs_through_keys.py`
- `tests/tabs/test_ungroup_tabs.py`
