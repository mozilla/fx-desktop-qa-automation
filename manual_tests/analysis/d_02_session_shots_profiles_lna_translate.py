from _ledger import C

# ---------------------------------------------------------------- suite 68
# "Session Restore" (67 cases) - tree has 226 browser-chrome sessionstore tests
C(
    68,
    "STRONG",
    "browser/components/sessionstore/test/browser_restoreLastClosedTabOrWindowOrSession.js; "
    "browser_restoreLastActionCorrectOrder.js; browser_undoCloseById.js; browser_undoCloseById_targetWindow.js",
    "VERIFIED: this file's add_tasks are test_undo_last_action (tab+window), test_forget_closed_window, "
    "test_user_clears_history, test_reopen_last_tab_if_no_closed_actions, "
    "test_reopen_last_session_if_no_closed_actions - the whole Ctrl+Shift+T ladder.",
    [
        117047,   # closed tabs restored by keyboard shortcut
        463046,   # recently closed tabs can be restored
        2186610,  # last closed tab restored by keyboard shortcut
        2186918,  # last closed window restored by keyboard shortcut
        2186919,  # last closed session restored by keyboard shortcut
        2191112,  # clearing browsing data/history resets last closed actions
        2197845,  # keyboard shortcut restores multiple closed tabs
        2197846,  # keyboard shortcut restores multiple closed windows
    ],
)
C(
    68,
    "STRONG",
    "browser/components/sessionstore/test/browser_aboutSessionRestore.js; browser_aboutRestartrequired_noRestore.js",
    "about:sessionrestore page: tab/window tree selection and both restore buttons.",
    [116973, 114832, 114834, 114836],
)
C(
    68,
    "STRONG",
    "browser/components/sessionstore/test/browser_pinned_tabs.js; browser_586068-apptabs.js; "
    "browser_586068-apptabs_ondemand.js; browser_restore_verticalPinnedTabs.js",
    "Pinned/app tabs are restored, including the vertical-tabs layout.",
    [114816, 2198150, 2198377, 2333487],
)
C(
    68,
    "STRONG",
    "browser/components/sessionstore/test/browser_scrollPositions.js; browser_scrollPositionsReaderMode.js",
    "Scroll position persistence per tab/frame.",
    [114827],
)
C(
    68,
    "STRONG",
    "browser/components/sessionstore/test/browser_formdata.js; browser_formdata_xpath.js; "
    "browser_formdata_format.js; browser_formdata_max_size.js; browser_formdata_password.js",
    "Form-input restore has five dedicated tests.",
    [114830, 117515],
)
C(
    68,
    "STRONG",
    "browser/components/sessionstore/test/browser_1446343-windowsize.js; browser_restored_window_features.js; "
    "browser_586068-window_state.js",
    "Window width/height/position/features restore.",
    [114826],
)
C(
    68,
    "STRONG",
    "browser/components/privatebrowsing/test/browser/browser_privatebrowsing_noSessionRestoreMenuOption.js",
    "'Restore Previous Session' hidden in a private window.",
    [115426],
)
C(
    68,
    "STRONG",
    "browser/components/sessionstore/test/browser_closed_tabs_windows.js; browser_closed_tabs_closed_windows.js; "
    "browser_closed_objects_changed_notifications_tabs.js; browser_closed_objects_changed_notifications_windows.js; "
    "browser_forget_closed_tab_window_byId.js; "
    "browser/components/firefoxview/tests/browser/browser_recentlyclosed_firefoxview.js",
    "Cross-window recently-closed bookkeeping, dismissal and the Firefox View surface.",
    [2333476, 2333480, 2333482, 2333484, 2333486],
)
C(
    68,
    "STRONG",
    "browser/components/customizableui/test/browser_history_recently_closed.js",
    "Recently-closed tabs/windows in the History menu and hamburger menu.",
    [117049, 117178, 2333477, 2333478],
)
C(
    68,
    "MEDIUM",
    "browser/components/sessionstore/test/browser_crashedTabs.js; browser_background_tab_crash.js; "
    "browser_394759_purge.js; browser_248970_b_perwindowpb.js; browser_windowRestore_perwindowpb.js; "
    "browser_restore_tabless_window.js",
    "Crash restore, private-window exclusion, per-window restore and the history-setting matrices "
    "are automated in narrower forms than the manual cases describe.",
    [114828, 117040, 2333481, 2333483, 2333485, 2198152, 2198153, 2191113,
     116003, 171451, 1592228, 1569299, 1569329, 114837, 114844],
)

# ---------------------------------------------------------------- suite 943
# "Screenshots" (48 cases) - tree has 30 browser-chrome screenshots tests
C(
    943,
    "STRONG",
    "browser/components/screenshots/tests/browser/browser_screenshots_test_toggle_pref.js",
    "Enabling/disabling Screenshots through the pref.",
    [56213],
)
C(
    943,
    "STRONG",
    "browser/components/screenshots/tests/browser/browser_screenshots_drag_test.js; "
    "browser_screenshots_drag_scroll_test.js; browser_test_selection_size_text.js; browser_test_resize.js; "
    "browser_test_element_picker.js; browser_shadowRoot_test.js; browser_iframe_test.js",
    "Region selection by drag, click-to-pick-element, resizing the selection and the size readout.",
    [56215, 56217, 2628709, 2628710],
)
C(
    943,
    "STRONG",
    "browser/components/screenshots/tests/browser/browser_screenshots_test_full_page.js; "
    "browser_screenshots_test_visible.js; browser_screenshots_test_downloads.js; browser_screenshots_download_filenames.js",
    "'Save full page' / 'Save visible' capture and the resulting download (incl. filename handling).",
    [56216, 463287, 2628707, 2628708, 2628713, 2628723],
)
C(
    943,
    "STRONG",
    "browser/components/screenshots/tests/browser/browser_keyboard_shortcuts.js",
    "VERIFIED: add_tasks are test_download_shortcut and test_copy_shortcut - Ctrl/Cmd+S and Ctrl/Cmd+C "
    "on the preview, asserting the download succeeds / the clipboard is written.",
    [2628727, 2628728, 2628714],
)
C(
    943,
    "STRONG",
    "browser/components/screenshots/tests/browser/browser_screenshots_test_toolbar_button.js",
    "Toolbar 'Take a Screenshot' button entry point.",
    [2628704],
)
C(
    943,
    "STRONG",
    "browser/components/urlbar/tests/browser-quickactions/browser_screenshot.js",
    "Screenshot invoked from the urlbar quick action.",
    [2628705],
)
C(
    943,
    "STRONG",
    "browser/components/screenshots/tests/browser/browser_screenshots_downloads_private.js",
    "Screenshots taken and saved from a private window.",
    [2628706],
)
C(
    943,
    "STRONG",
    "browser/components/screenshots/tests/browser/browser_screenshots_telemetry_tests.js",
    "Initiation / copy / download / selection-type counters.",
    [2628698, 2628699, 2628700, 2628701],
)
C(
    943,
    "STRONG",
    "browser/components/screenshots/tests/browser/browser_overlay_keyboard_test.js; browser_keyboard_tests.js; "
    "browser_screenshots_focus_test.js; browser_screenshots_face_focusable.js; browser_screenshots_test_escape.js",
    "Keyboard navigation of the overlay, Shift+arrow selection resizing, focus order and Escape/close.",
    [2628738, 2628739, 2628712],
)
C(
    943,
    "STRONG",
    "browser/components/screenshots/tests/browser/browser_screenshots_test_screenshot_too_big.js; "
    "browser_screenshots_short_page_test.js",
    "Over-max-size and very short pages.",
    [2628725, 2628734],
)
C(
    943,
    "MEDIUM",
    "browser/components/screenshots/tests/browser/browser_test_moving_tab_to_new_window.js; "
    "browser_screenshots_page_unload.js; browser_screenshots_overlay_panel_sync.js; browser_screenshots_splitview.js; "
    "browser_screenshots_test_page_crash.js",
    "Multi-tab/window lifecycle is automated but not the manual multi-tab management case; "
    "the context-menu entry, Retry button and save-to-custom-location are not automated.",
    [2628724, 2628703, 2628711, 2628715],
)

# ---------------------------------------------------------------- suite 2119
# "Profiles" (56 cases). Only the SelectableProfiles sections (662448/662449) map;
# the about:profiles / Profile-Manager / command-line sections do not.
C(
    2119,
    "STRONG",
    "browser/components/profiles/tests/browser/browser_test_profile_selector.js; browser_appmenu.js; "
    "browser_appmenu_menuitem_updates.js; browser_menubar_profiles.js",
    "Profile selector, app-menu entry and the Menu Bar 'Profiles' item.",
    [3198069, 3198074, 3198075],
)
C(
    2119,
    "STRONG",
    "browser/components/profiles/tests/browser/browser_create_profile_page_test.js; browser_activate.js; "
    "browser_empty_name_beforeunload_test.js",
    "New-profile page: displayed, profile created, appears in the list, empty-name guard.",
    [3198070, 3198071, 3198076],
)
C(
    2119,
    "STRONG",
    "browser/components/profiles/tests/browser/browser_edit_profile_test.js; browser_delete_profile_page_test.js; "
    "browser_fxa_menu_profiles.js",
    "Edit-profile and delete-profile pages, including the FxA-signed-in variant.",
    [3198072, 3198073, 3198077, 3198078],
)
C(
    2119,
    "STRONG",
    "browser/components/profiles/tests/browser/browser_icon_avatar_test.js; browser_custom_avatar_test.js",
    "Avatar picker: built-in icon selection and custom image upload.",
    [3198081, 3198082],
)
C(
    2119,
    "STRONG",
    "browser/components/profiles/tests/browser/browser_preferences.js",
    "'Manage profiles' entry and the Profiles section in about:preferences#general.",
    [3198080, 3198083],
)
C(
    2119,
    "MEDIUM",
    "browser/components/profiles/tests/browser/browser_edit_profile_theme_picker_nova_test.js; "
    "browser_update_profile_on_window_switch.js; browser_notify_changes.js; browser_window_title_test.js; "
    "browser_desktop_shortcut_test.js; browser_test_last_tab.js; browser_moveTabToProfile.js; browser_refresh_button.js",
    "Theme picker and cross-window profile sync are automated, but the manual cases here are "
    "OS-theme / taskbar-appearance and multi-device checks.",
    [3198084, 3198085, 3198066, 3198067, 3198079],
)
C(
    2119,
    "MEDIUM",
    "toolkit/profile/test/chrome/test_create_profile.xhtml; toolkit/profile/test/; browser/components/profiles/tests/browser/browser_activate.js",
    "The legacy about:profiles / Profile Manager / command-line sections are covered only at "
    "xpcshell level, with no UI driving.",
    [130769, 130789, 130791, 130792, 130906, 130907, 136412],
)

# ---------------------------------------------------------------- suite 69070
# "Local Network Access / Local Device Access" (37 cases)
C(
    69070,
    "STRONG",
    "netwerk/test/browser/browser_test_local_network_access_permissions.js; browser_test_local_network_access.js; "
    "browser_test_local_network_access_basic.js; browser_test_local_network_access_navigation.js; "
    "browser_test_lna_insecure_context.js; browser_test_lna_worker.js; browser_test_local_network_access_websocket.js",
    "VERIFIED: the permissions test drives the real doorhanger - allow, deny, 'remembered' inside the "
    "expiry window and re-prompt after expiry, for both loopback and local-network address spaces.",
    [
        3155248,  # LNA prompt correctly displayed
        3155250,  # LNA can be allowed
        3155251,  # LNA can be blocked
        3155253,  # LNA decision can be remembered
        3155948,  # Local Device Access prompt correctly displayed
        3155950,  # Local Device Access can be allowed
        3155951,  # Local Device Access can be blocked
        3155952,  # Local Device Access decision can be remembered
        3168990,  # new Local Device Access request blocked automatically
        3155958,  # new Local Device Access request blocked automatically (device section)
    ],
)
C(
    69070,
    "STRONG",
    "netwerk/test/browser/browser_test_local_network_access_telemetry.js; "
    "netwerk/test/unit/test_ip_address_space_lna_glean.js",
    "Allowed/blocked telemetry for both network and device access.",
    [3155257, 3155258, 3155968, 3155969],
)
C(
    69070,
    "MEDIUM",
    "netwerk/test/browser/browser_test_local_network_access_feature_policy.js; browser_test_local_network_trackers.js; "
    "browser_test_local_network_access_sni_leak.js; netwerk/test/unit/test_lna_captive_portal.js",
    "Feature-policy, tracker and captive-portal edges are automated; the PBM variants, "
    "about:preferences surface, restart persistence and a11y/RTL matrix are not.",
    [3155255, 3155254, 3155252, 3155949, 3155953, 3155954],
)

# ---------------------------------------------------------------- suite 71394
# "Translate quick action / about:translations" (40 cases)
C(
    71394,
    "STRONG",
    "browser/components/urlbar/tests/browser-quickactions/browser_translate.js; browser_general.js",
    "The 'translate' quick action: shown for the full keyword, not shown for an invalid one, "
    "and opening about:translations.",
    [3255681, 3255682, 3255736, 3255731],
)
C(
    71394,
    "STRONG",
    "toolkit/components/translations/tests/browser/browser_about_translations_url_load.js; "
    "browser_about_translations_url_update.js; browser_about_translations_hash_updates.js; "
    "browser_about_translations_scheduling.js",
    "about:translations initial state from URL/hash, request scheduling and the in-progress state.",
    [3255734, 3255738, 3255739],
)
C(
    71394,
    "STRONG",
    "toolkit/components/translations/tests/browser/browser_about_translations_dropdowns.js; "
    "browser_about_translations_swap_languages_button_explicit.js; "
    "browser_about_translations_swap_languages_button_detected.js; "
    "browser_about_translations_flip_lexical_shortlist.js",
    "Source/target language dropdowns and the swap-languages button (explicit and auto-detected).",
    [3256453, 3256473, 3255735],
)
C(
    71394,
    "STRONG",
    "toolkit/components/translations/tests/browser/browser_about_translations_source_clear_button_functionality.js; "
    "browser_about_translations_source_clear_button_visibility.js; "
    "browser_about_translations_copy_button_functionality.js; "
    "browser_about_translations_copy_button_enabled_states.js",
    "Clear-input 'X' button and copy button, functionality plus enabled/visible states.",
    [3256460],
)
C(
    71394,
    "STRONG",
    "toolkit/components/translations/tests/browser/browser_about_translations_resize_sections_by_input.js; "
    "browser_about_translations_resize_sections_by_window.js; browser_about_translations_resize_sections_by_zoom.js; "
    "browser_about_translations_resize_sections_with_messages.js",
    "Panel responsiveness: growth by input, by window resize and by zoom.",
    [3261569, 3256459],
)
C(
    71394,
    "STRONG",
    "toolkit/components/translations/tests/browser/browser_about_translations_translate_error.js; "
    "browser_about_translations_detected_language_unsupported.js",
    "'There was a problem translating' and the unsupported-language message.",
    [3256458, 3256472],
)
C(
    71394,
    "STRONG",
    "toolkit/components/translations/tests/browser/browser_about_translations_telemetry_open.js; "
    "browser_about_translations_telemetry_copy_button.js; browser_about_translations_telemetry_swap_button.js; "
    "browser_about_translations_telemetry_translation_request.js; "
    "browser_about_translations_telemetry_clear_source_text_button.js; "
    "browser_about_translations_telemetry_standalone_messages.js; "
    "browser_about_translations_telemetry_unsupported_language_message.js; "
    "browser_about_translations_telemetry_feature_blocked_info_message.js",
    "Eight dedicated telemetry tests cover the whole event set for this page.",
    [3261566],
)
C(
    71394,
    "STRONG",
    "toolkit/components/translations/tests/browser/browser_about_translations_tab_focus_order.js; "
    "browser_about_translations_accessible_invocation.js",
    "Tab focus order and accessible invocation of every control on the page.",
    [3256479],
)
C(
    71394,
    "MEDIUM",
    "toolkit/components/translations/tests/browser/browser_about_translations_enabling.js; "
    "browser_about_translations_app_menu.js; browser_about_translations_directions.js; "
    "browser_about_translations_telemetry_feature_blocked_info_message.js",
    "Pref/policy gating and text direction are automated at a different granularity than the "
    "manual policy / RTL-build / locale cases.",
    [3310500, 3820989, 3311037, 3820971, 3820972, 3256481, 3256455, 3256456,
     3256457, 3256461, 3256477, 3256474, 3256478, 3371297],
)