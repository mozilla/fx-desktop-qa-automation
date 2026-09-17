"""Round 5 -- the remaining STARfox suites.

notifications (13), preferences (8), menus (7), audio_video (6), networking (6),
scrolling_panning_zooming (5), drag_and_drop (5), session_restore (5), find_toolbar (3),
reader_view (3), geolocation (2), theme_and_toolbar (2), printing_ui (2),
language_packs (2), profile (1).

Two notable shapes here:

* tests/notifications is really a permission-prompt suite (camera, microphone, screen share,
  geolocation, add-on install), and browser/base/content/test/webrtc/ plus
  browser/base/content/test/permissions/ cover it closely.
* tests/networking is a DoH suite, and toolkit/components/doh/test/browser/ has 14 tests that
  match it almost row for row -- including provider steering, which is exactly the
  "Cloudflare / NextDNS as provider" pair.

tests/drag_and_drop is the exception: it copies table structures between Firefox and other
applications, which the tree cannot reach.
"""

from ledger import T

WEBRTC = "browser/base/content/test/webrtc/"
PERM = "browser/base/content/test/permissions/"
DOH = "toolkit/components/doh/test/browser/"
ZOOM = "browser/base/content/test/zoom/"
READER = "toolkit/components/reader/tests/browser/"
CM = "browser/base/content/test/contextMenu/"
SS = "browser/components/sessionstore/test/"
PRINT = "toolkit/components/printing/tests/"
DL = "browser/components/downloads/test/browser/"

N = "tests/notifications/"
PR = "tests/preferences/"
M = "tests/menus/"
AV = "tests/audio_video/"
NW = "tests/networking/"
Z = "tests/scrolling_panning_zooming/"
DD = "tests/drag_and_drop/"
SR = "tests/session_restore/"
FT = "tests/find_toolbar/"
RV = "tests/reader_view/"
G = "tests/geolocation/"
TT = "tests/theme_and_toolbar/"
PU = "tests/printing_ui/"
LP = "tests/language_packs/"
PF = "tests/profile/"

# ================================================================ notifications / permissions
T(
    "STRONG",
    WEBRTC + "browser_devices_get_user_media.js; "
    "browser_devices_get_user_media_default_permissions.js; browser_webrtc_hooks.js",
    "browser_devices_get_user_media.js walks the camera-only, microphone-only and combined "
    "audio+video prompts and asserts both the allow and deny outcomes.",
    [
        N + "test_camera_permissions_notification.py",
        N + "test_microphone_permissions_notification.py",
        N + "test_audio_video_permissions_notification.py",
    ],
)
T(
    "STRONG",
    WEBRTC + "browser_devices_get_user_media_screen.js; "
    "browser_devices_get_user_media_screen_tab_close.js",
    "The screen/window share picker and its deny path.",
    [
        N + "test_screen_share_permission_prompt.py",
        N + "test_deny_screen_capture.py",
    ],
)
T(
    "STRONG",
    PERM
    + "browser_permission_delegate_geo.js; browser_geolocation_replaced_prompt.js; "
    "dom/geolocation/test/browser/browser_bug1008941_dismissGeolocationHanger.js",
    "The geolocation prompt appearing, being dismissed and being denied are each covered.",
    [
        N + "test_geolocation_prompt_presence.py",
        N + "test_deny_geolocation.py",
    ],
)
T(
    "STRONG",
    PERM + "browser_permissions.js; browser_permissions_postPrompt.js; "
    "browser_permissions_handling_user_input.js",
    "The generic notification / permission panel and its presentation.",
    [N + "test_notifications_displayed.py"],
)
T(
    "STRONG",
    "toolkit/mozapps/extensions/test/browser/browser_webapi_install.js; "
    "browser_local_install.js; browser_webapi_install_disabled.js",
    "The add-on install flow, its confirmation prompt, the completion notification and the "
    "cancel path.",
    [
        N + "test_webextension_completed_installation_successfully_displayed.py",
        N + "test_cancel_webextension.py",
    ],
)
T(
    "STRONG",
    DL + "browser_downloads_panel_opens.js; browser_first_download_panel.js; "
    "browser_overflow_anchor.js; browser_downloads_autohide.js",
    "The downloads button appearing when a download starts and its finished state.",
    [
        N + "test_downloads_button_is_displayed.py",
        N + "test_downloads_finished_button_is_displayed.py",
    ],
)

# ================================================================ DoH / networking
T(
    "STRONG",
    DOH + "browser_providerSteering.js; browser_trrSelect.js; browser_doh_region.js; "
    "browser_remoteSettings_rollout.js",
    "browser_providerSteering.js is dedicated to which TRR provider is selected and steered to, "
    "which is exactly the default-Cloudflare / NextDNS / custom-provider trio.",
    [
        NW + "test_cloudflare_as_default_doh_provider.py",
        NW + "test_nextdns_as_doh_provider.py",
        NW + "test_custom_doh_provider.py",
    ],
)
T(
    "STRONG",
    DOH + "browser_throttle_heuristics.js; browser_userInterference.js; "
    "browser_trrSelection_disable.js; browser_policyOverride.js",
    "browser_throttle_heuristics.js covers the heuristics being skipped once TRR mode is set "
    "explicitly, which is the assertion this test makes.",
    [NW + "test_heuristics_disabled_when_trr_mode_2.py"],
)
T(
    "STRONG",
    DOH
    + "browser_cleanFlow.js; browser_dirtyEnable.js; browser_remoteSettings_newProfile.js; "
    "browser_rollback.js",
    "The default DNS-protection state on a fresh and on a dirty profile.",
    [NW + "test_default_dns_protection.py"],
)
T(
    "STRONG",
    "browser/base/content/test/siteIdentity/browser_check_identity_state.js; "
    "dom/security/test/https-first/browser_httpsfirst.js",
    "Loading a plain HTTP site and the resulting identity state.",
    [NW + "test_http_site.py"],
)

# ================================================================ audio / video
T(
    "STRONG",
    PERM + "browser_autoplay_blocked.js; "
    "dom/media/autoplay/test/browser/browser_autoplay_policy_request_permission.js; "
    "browser_autoplay_policy_detection_global_and_site_sticky.js",
    "The blocked-autoplay doorhanger and the Allow / Block choices, with the sticky permission "
    "asserted afterwards.",
    [
        AV + "test_allow_audio_video_functionality.py",
        AV + "test_block_audio_video_functionality.py",
    ],
)
T(
    "STRONG",
    "browser/components/preferences/tests/privacy/browser_privacy_status_card.js; "
    + PERM
    + "browser_autoplay_blocked.js",
    "The autoplay entry in the permissions section of about:preferences.",
    [AV + "test_autoplay_permission_settings_displayed.py"],
)
T(
    "STRONG",
    "toolkit/content/tests/browser/browser_delay_autoplay_media.js; "
    "browser_delay_autoplay_playAfterTabVisible.js; "
    "browser_delay_autoplay_playMediaInMuteTab.js; browser_delay_autoplay_multipleMedia.js",
    "Autoplay being deferred while the tab is in the background and resuming when it becomes "
    "visible.",
    [AV + "test_autoplay_sound_blocking_background_tab.py"],
)
T(
    "STRONG",
    "dom/media/autoplay/test/browser/browser_autoplay_policy_detection_global_sticky.js; "
    "browser_autoplay_policy_play_twice.js; browser_autoplay_userinteraction.js",
    "The user's allow/block decision surviving a reload is the sticky-permission behaviour these "
    "tests assert.",
    [AV + "test_users_actions_saved_on_reload.py"],
)
T(
    "STRONG",
    "toolkit/content/tests/widgets/test_videocontrols.html; "
    "test_videocontrols_keyhandler.html; test_videocontrols_audio.html",
    "The HTML5 video control set and its keyboard handling are covered by the videocontrols "
    "widget tests.",
    [AV + "test_html5_video_playback_controls.py"],
)

# ================================================================ zoom
T(
    "STRONG",
    ZOOM + "browser_default_zoom.js; browser_default_zoom_sitespecific.js; "
    "browser_default_zoom_multitab.js",
    "The default zoom level persisting across sites and tabs.",
    [Z + "test_default_zoom_persists.py"],
)
T(
    "STRONG",
    ZOOM
    + "browser_mousewheel_zoom.js; browser_keyboard_mousewheel_zoom_consistency.js",
    "Ctrl+wheel zoom and its consistency with the keyboard shortcuts.",
    [Z + "test_mouse_wheel_zoom.py"],
)
T(
    "STRONG",
    ZOOM + "browser_zoom_commands.js; "
    "browser/modules/test/browser/browser_urlBar_zoom.js; "
    "browser/components/customizableui/test/browser_947914_button_zoomIn.js",
    "The View > Zoom commands and the urlbar indicator that tracks them.",
    [
        Z + "test_zoom_from_menu_bar.py",
        Z + "test_zoom_menu_correlation.py",
    ],
)
T(
    "STRONG",
    ZOOM + "browser_subframe_textzoom.js; browser_zoom_commands.js",
    "Zoom Text Only and its effect on subframes.",
    [Z + "test_zoom_text_only.py"],
)

# ================================================================ menus
T(
    "STRONG",
    CM + "browser_contextmenu.js; browser_contextmenu_linkopen.js; "
    "browser_contextmenu_bookmark_link_text.js",
    "browser_contextmenu.js declares and asserts the expected item list for a hyperlink, and "
    "browser_contextmenu_linkopen.js drives its open actions.",
    [M + "test_hyperlink_context_menu.py"],
)
T(
    "STRONG",
    CM + "browser_contextmenu.js; browser_view_image.js; browser_save_image.js; "
    "browser_copy_image_link.js",
    "The image context menu's item list plus a test per principal action.",
    [M + "test_image_context_menu_actions.py"],
)
T(
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_tab_groups_tabContextMenu.js; "
    "browser_tabswitch_contextmenu.js; browser_multiselect_tabs_move_to_new_window_contextmenu.js; "
    "browser_close_tab_by_dblclick.js",
    "The tab context menu's actions, including close, are covered by the tab context-menu tests.",
    [
        M + "test_tab_context_menu_actions.py",
        M + "test_tab_context_menu_close.py",
    ],
)
T(
    "STRONG",
    CM + "browser_contextmenu_input.js; browser_contextmenu_contenteditable.js; "
    "browser/components/customizableui/test/browser_947914_button_copy.js; "
    "browser_947914_button_cut.js; browser_947914_button_paste.js",
    "Copy / cut / paste from the field context menu and from the panel buttons.",
    [M + "test_copy_paste_actions.py"],
)
T(
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_new_tab_url.js; "
    "browser/components/customizableui/test/browser_newtab_button_customizemode.js",
    "The New Tab label / button and the tab it opens.",
    [M + "test_new_tab_label.py"],
)

# ================================================================ session restore
T(
    "STRONG",
    SS
    + "browser_closed_tabs_windows.js; browser_closed_objects_changed_notifications_tabs.js; "
    "browser_closedId.js; "
    "browser/components/firefoxview/tests/browser/browser_recentlyclosed_firefoxview.js",
    "test_ClosedTabMethods builds closed tabs across several windows and asserts the aggregated "
    "list each window sees; the Firefox View test covers the same set surfaced in that panel.",
    [
        SR
        + "test_closed_tabs_from_multiple_windows_shown_in_fx_view_corresponding_section.py",
        SR + "test_closed_tabs_from_multiple_windows_shown_in_history_menu_bar.py",
        SR + "test_closed_tabs_from_multiple_windows_shown_in_library_menu.py",
    ],
)
T(
    "STRONG",
    SS + "browser_restoreLastClosedTabOrWindowOrSession.js; "
    "browser_restoreLastActionCorrectOrder.js; browser_undoCloseById.js",
    "Restoring the last closed tab by keyboard shortcut, and the ordering when several were "
    "closed.",
    [SR + "test_restore_last_closed_tabs_shortcut.py"],
)
T(
    "STRONG",
    SS
    + "browser_forget_closed_tab_window_byId.js; browser_forget_async_closings.js; "
    + "browser/components/firefoxview/tests/browser/browser_recentlyclosed_firefoxview.js",
    "test_dismiss_tab and the forget-by-id tests cover a restored or dismissed tab leaving the "
    "recently-closed list.",
    [SR + "test_restored_closed_tabs_removed_from_all_history_entries.py"],
)

# ================================================================ find toolbar
T(
    "STRONG",
    "toolkit/content/tests/browser/browser_findbar.js; browser_findbar_marks.js; "
    "browser/base/content/test/general/browser_findbarClose.js",
    "browser_findbar.js drives find over page content and asserts the match count and "
    "highlights; browser_findbarClose.js covers the navigation controls and dismissal.",
    [
        FT + "test_find_toolbar_search.py",
        FT + "test_find_toolbar_nav.py",
    ],
)
T(
    "STRONG",
    "toolkit/components/pdfjs/test/browser_pdfjs_find.js",
    "Six tasks cover find inside a PDF, including the not-found and wrap-around states.",
    [FT + "test_find_in_pdf.py"],
)

# ================================================================ reader view
T(
    "STRONG",
    READER
    + "browser_readerMode.js; browser_readerMode_cached.js; browser_readerMode_refresh.js",
    "Entering reader mode from the urlbar button and the resulting about:reader URL.",
    [RV + "test_reader_view_location_bar.py"],
)
T(
    "STRONG",
    READER + "browser_readerMode_menu.js; browser_readerMode_colorSchemePref.js; "
    "browser_readerMode_customColorScheme.js; browser_readerMode_readingTime.js",
    "The reader type-control panel -- font, size, colour scheme -- is covered by the menu and "
    "colour-scheme tests.",
    [RV + "test_improved_type_control_panel.py"],
)

# ================================================================ geolocation
T(
    "STRONG",
    "dom/geolocation/test/mochitest/test_allowCurrent.html; test_allowWatch.html; "
    "test_cachedPosition.html; "
    "dom/geolocation/test/browser/browser_geolocation_override.js",
    "The W3C geolocation API's getCurrentPosition and watchPosition paths, with a mocked "
    "provider, are covered by the geolocation mochitests.",
    [
        G + "test_geolocation_shared_via_w3c_api.py",
        G + "test_geolocation_shared_via_html5.py",
    ],
)

# ================================================================ theme and toolbar
T(
    "STRONG",
    "browser/themes/test/browser/browser_BuiltInThemes_installs.js; "
    "toolkit/components/extensions/test/browser/browser_ext_themes_lwtsupport.js; "
    "browser_ext_themes_persistence.js; browser_ext_themes_dynamic_updates.js",
    "Installing and enabling a theme and the resulting chrome colours.",
    [
        TT + "test_customize_themes_and_redirect.py",
        TT + "test_installed_theme_enabled.py",
    ],
)

# ================================================================ printing
T(
    "STRONG",
    PRINT
    + "browser_modal_print.js; browser_preview_navigation.js; browser_modal_resize.js; "
    "browser_print_stream.js",
    "The print modal and its preview, including navigating the previewed pages.",
    [PU + "test_print_preview.py"],
)
T(
    "STRONG",
    PRINT + "browser_pdf_printer_settings.js; browser_print_stream.js; "
    "browser_pdf_hidden_settings.js",
    "testPDFPrinterSettings and testPDFFile print through the Print to PDF destination and "
    "assert the emitted stream.",
    [PU + "test_print_to_pdf.py"],
)

# ================================================================ preferences
T(
    "STRONG",
    "browser/components/preferences/tests/home/browser_homepage_firefox_home.js; "
    "browser_homepage_default.js; browser_homepage_homepage.js; "
    "browser_homepage_firefox_home_disabled_both_off.js",
    "The Firefox Home settings for new windows and new tabs, and what loads on launch.",
    [
        PR + "test_firefox_home_new_tabs.py",
        PR + "test_firefox_home_on_launch.py",
    ],
)
T(
    "STRONG",
    "browser/base/content/test/siteIdentity/browser_identityPopup_clearSiteData.js; "
    "browser/base/content/test/sanitize/browser_sanitize-cookie-exceptions.js; "
    "browser/components/preferences/tests/etp/browser_cookies_exceptions.js; "
    "browser_cookie_exceptions_addRemove.js",
    "Clearing and managing cookies and site data from about:preferences.",
    [
        PR + "test_clear_cookie_data.py",
        PR + "test_manage_cookie_data.py",
    ],
)
T(
    "STRONG",
    "browser/components/privatebrowsing/test/browser/browser_privatebrowsing_crh.js; "
    "browser/components/preferences/tests/privacy/browser_privacy_history_search_l10n_ids.js",
    "The 'Never remember history' mode and the always-private behaviour it produces.",
    [PR + "test_never_remember_history.py"],
)
T(
    "STRONG",
    "browser/components/preferences/tests/privacy/browser_privacy_status_card.js; "
    + PERM
    + "browser_permissions.js; browser_notification_permission_telemetry.js",
    "The notification-permission setting in about:preferences and its effect on the prompt.",
    [PR + "test_notifications_change_set.py"],
)
T(
    "STRONG",
    "toolkit/mozapps/extensions/test/xpcshell/test_webextension_langpack.js; "
    "test_distribution_langpack.js; "
    "browser/components/preferences/tests/languages/browser_languages_subdialog.js; "
    "browser_browser_languages_subdialog.js; browser_languages_pane.js",
    "Installing a language pack and switching the browser language from about:preferences.",
    [
        PR + "test_lang_pack_changed_from_about_prefs.py",
        LP + "test_language_pack_install_addons.py",
        LP + "test_language_pack_install_preferences.py",
    ],
)

# ================================================================ partial / unique
T(
    "PARTIAL",
    "toolkit/mozapps/update/tests/browser/browser_aboutDialog_fc_check_noUpdate.js; "
    "browser_aboutPrefs_fc_check_noUpdate.js",
    "The update-check UI in about:preferences has in-tree tests, but they drive a mocked update "
    "server; this STARfox test exercises the real check against the live AUS endpoint.",
    [PR + "test_check_for_updates.py"],
)
T(
    "PARTIAL",
    CM + "browser_contextmenu.js",
    "browser_contextmenu.js asserts the full item list of each content context menu, which "
    "overlaps this test, but the 'frequently used' reordering behaviour itself is not asserted.",
    [M + "test_frequently_used_context_menu.py"],
)
T(
    "PARTIAL",
    "browser/components/profiles/tests/browser/browser_test_profile_selector.js; "
    "browser_create_profile_page_test.js; browser_delete_profile_page_test.js",
    "Profile creation and deletion are covered in tree, and browser_test_profile_selector.js "
    "covers activating one, but nothing asserts which profile is marked as the default to launch.",
    [PF + "test_set_default_profile.py"],
)
T(
    "PARTIAL",
    READER + "browser_readerMode.js; "
    "browser/components/sidebar/tests/browser/browser_hide_sidebar.js",
    "Reader mode and sidebar hiding are each covered, but not the interaction where entering "
    "reader view collapses an open sidebar.",
    [RV + "test_reader_view_close_sidebar.py"],
)
T(
    "UNIQUE",
    "n/a",
    "Copying table structure between applications: whole rows and columns, table headers, "
    "hyperlinks inside table cells, and pasting into and out of a third-party editor. In-tree "
    "clipboard tests stay inside Firefox, so none of these cross-application transfers has a "
    "counterpart.",
    [
        DD + "test_copy_entire_row_column.py",
        DD + "test_copy_table_header.py",
        DD + "test_copy_hyperlink_table.py",
        DD + "test_copy_from_an_editor_paste_in_another.py",
        DD + "test_paste_image_text.py",
    ],
)
T(
    "UNIQUE",
    "n/a",
    "Geolocation shared with a live third-party endpoint (browserleaks). The tree's geolocation "
    "tests use a mocked provider and never leave the harness.",
    [N + "test_geolocation_allow_browserleaks.py"],
)
