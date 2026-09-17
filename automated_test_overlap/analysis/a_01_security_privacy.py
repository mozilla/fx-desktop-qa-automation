"""Round 5 -- tests/security_and_privacy (60 linked STARfox tests).

This is the STARfox suite with the most in-tree competition. Two tree directories do almost
all the work:

* browser/base/content/test/protectionsUI/ -- 24 browser-chrome tests for the shield /
  trust panel, one per blockable category and one per panel state.
* browser/components/privatebrowsing/test/browser/ -- 45 tests for private browsing,
  including browser_privatebrowsing_resetPBM.js for the newer "end private session" feature.

Plus browser/base/content/test/siteIdentity/ (35 tests) for the connection-state and
certificate half of the panel.

One real difference worth recording: many of these STARfox tests navigate to **live external
URLs** (senglehardt.com tracking-test pages, httpforever.com), where the in-tree tests use a
local test server with fabricated tracker entries. Same flow, but the STARfox versions carry a
network dependency the tree ones do not.
"""

from ledger import T

PUI = "browser/base/content/test/protectionsUI/"
PBM = "browser/components/privatebrowsing/test/browser/"
SID = "browser/base/content/test/siteIdentity/"
SP = "tests/security_and_privacy/"

# ================================================================ trust panel: categories
T(
    "STRONG",
    PUI + "browser_protectionsUI_cryptominers.js; browser_protectionsUI_categories.js; "
    "browser_protectionsUI_state.js",
    "browser_protectionsUI_cryptominers.js loads a cryptomining resource, asserts it was "
    "blocked, opens the panel and checks the category is listed -- and repeats with the "
    "category unchecked in preferences, which is the blocked / not-blocked pair these three "
    "STARfox tests split across.",
    [
        SP + "test_cryptominers_blocked_and_shown_in_info_panel.py",
        SP + "test_cryptominers_displayed_subpanel.py",
        SP + "test_cryptominers_subpanel_display_when_not_blocked.py",
    ],
)
T(
    "STRONG",
    PUI
    + "browser_protectionsUI_fingerprinters.js; browser_protectionsUI_categories.js; "
    "browser/components/preferences/tests/etp/browser_etp_customize_1.js",
    "browser_protectionsUI_fingerprinters.js covers the blocked and unblocked fingerprinter "
    "states in the panel, and the ETP preferences tests cover the checkbox that drives them.",
    [
        SP + "test_fingerprinters_blocked_and_shown_in_panel_and_preferences.py",
        SP + "test_fingerprinters_displayed_subpanel.py",
        SP + "test_fingerprinters_subpanel_display_when_not_blocked.py",
    ],
)
T(
    "STRONG",
    PUI + "browser_protectionsUI_suspicious_fingerprinters_subview.js; "
    "browser_protectionsUI_pbmode_exceptions.js; "
    "browser/components/preferences/tests/etp/browser_etp_customize_2.js",
    "A test dedicated to the suspected-fingerprinters subview, with the private-window variant "
    "covered by browser_protectionsUI_pbmode_exceptions.js -- the all-windows / private-only "
    "split these two tests draw.",
    [
        SP + "test_custom_block_suspected_fingerprinters_in_all_windows.py",
        SP + "test_custom_block_suspected_fingerprinters_only_in_private_windows.py",
    ],
)
T(
    "STRONG",
    PUI + "browser_protectionsUI_socialtracking.js",
    "Dedicated test for social-media trackers being blocked and surfaced in the panel subview.",
    [SP + "test_social_media_trackers_displayed_subpanel.py"],
)
T(
    "STRONG",
    PUI + "browser_protectionsUI_tracker_cookies_subview.js; "
    "browser_protectionsUI_cookies_subview.js",
    "Two tests for the cross-site tracking-cookies subview and its contents.",
    [SP + "test_cross_site_tracking_cookies_displayed_subpanel.py"],
)
T(
    "STRONG",
    PUI
    + "browser_protectionsUI_trackers_subview.js; browser_protectionsUI_categories.js; "
    "browser_protectionsUI_state.js",
    "browser_protectionsUI_trackers_subview.js opens the tracking-content subview and asserts "
    "its entries; browser_protectionsUI_categories.js covers the custom-mode configuration and "
    "the not-blocked rendering.",
    [
        SP + "test_tracking_content_custom_mode.py",
        SP + "test_tracking_content_subpanel_display_when_not_blocked.py",
        SP + "test_trackers_counted_correctly_in_panel.py",
        SP + "test_trackers_cryptominers_fingerprinters_blocked.py",
    ],
)

# ================================================================ trust panel: states
T(
    "STRONG",
    PUI + "browser_protectionsUI_state.js; browser_protectionsUI_shield_visibility.js; "
    "browser_protectionsUI_icon_state.js",
    "The no-trackers-detected state, and whether the shield is shown at all, are each covered "
    "by a dedicated test.",
    [
        SP + "test_no_trackers_detected.py",
        SP + "test_etp_panel_displayed_when_no_trackers_detected.py",
    ],
)
T(
    "STRONG",
    PUI + "browser_protectionsUI_state.js; browser_protectionsUI_categories.js; "
    "browser_protectionsUI_shield_visibility.js",
    "The panel's appearance with protection turned off, and with every category disabled in "
    "custom mode, are both asserted.",
    [
        SP + "test_etp_panel_displayed_when_protection_off.py",
        SP + "test_etp_panel_displayed_when_all_protections_disabled_custom.py",
    ],
)
T(
    "STRONG",
    PUI + "browser_protectionsUI.js; browser_protectionsUI_state.js; "
    "browser_protectionsUI_state_reset.js; browser_protectionsUI_fetch.js",
    "browser_protectionsUI.js toggles ETP for a site from the panel and asserts tracking "
    "content is then loaded rather than blocked, with state_reset covering the way back.",
    [
        SP + "test_etp_toggle_on_off_behavior.py",
        SP + "test_tracking_elements_not_blocked_with_etp_disabled.py",
    ],
)
T(
    "STRONG",
    PUI + "browser_protectionsUI_pbmode_exceptions.js",
    "Dedicated test for the ETP toggle's behaviour in a private window, including the exception "
    "not persisting.",
    [SP + "test_etp_toggle_on_off_behavior_private_window.py"],
)
T(
    "STRONG",
    PUI + "browser_protectionsUI_info_message.js",
    "browser_protectionsUI_info_message.js is specifically about the first-run informational "
    "state of the panel.",
    [SP + "test_ensure_panel_renders_on_first_run.py"],
)
T(
    "STRONG",
    PUI + "browser_protectionsUI_open_preferences.js; "
    "browser/components/protections/test/browser/browser_protections_report_ui.js",
    "The panel's links out -- to about:preferences#privacy and to the protections report -- are "
    "covered by browser_protectionsUI_open_preferences.js and the report UI test.",
    [
        SP + "test_protection_level_redirect_about_preferences.py",
        SP + "test_privacy_settings_footer_link_opens_correct_page.py",
        SP + "test_see_all_link_redirects_to_blocked_trackers.py",
    ],
)

# ================================================================ connection state / certs
T(
    "STRONG",
    SID + "browser_check_identity_state.js; browser_identity_UI.js; "
    "browser_identityBlock_focus.js",
    "browser_check_identity_state.js walks the identity block and popup across secure, "
    "insecure and mixed states, asserting the icon and the connection text for each -- the same "
    "assertions these four tests make one state at a time.",
    [
        SP + "test_connection_secure_second_level_panel.py",
        SP + "test_connection_not_secured_panel_for_http_sites.py",
        SP + "test_http_lock_icon_connection_state.py",
        SP + "test_secure_domain_certificate_messaging_panel.py",
    ],
)
T(
    "STRONG",
    SID + "browser_identityPopup_custom_roots.js; browser_identity_UI.js; "
    "browser_identityPopup_qwacs.js",
    "The extended / custom-root certificate messaging shown in the identity popup.",
    [SP + "test_extended_certificate_messaging_displayed_in_panel.py"],
)
T(
    "STRONG",
    SID + "browser_mixed_passive_content_indicator.js; browser_mcb_redirect.js; "
    "browser_mixedContentFramesOnHttp.js; browser_mixed_content_with_navigation.js",
    "Four tests cover the mixed-content warning appearing in the identity panel across passive "
    "content, redirects, frames and navigation.",
    [SP + "test_mixed_content_warning_displayed_in_panel.py"],
)
T(
    "STRONG",
    SID + "browser_deprecatedTLSVersions.js",
    "Dedicated test for the deprecated-TLS interstitial and which protocol versions are "
    "accepted.",
    [SP + "test_tls_v1_2_protocol.py"],
)
T(
    "STRONG",
    "browser/base/content/test/about/browser_aboutCertError.js; "
    "browser_aboutCertError_exception.js; browser_aboutCertError_telemetry.js",
    "The expired-certificate interstitial and its detail panel are covered by the "
    "about:certerror test group.",
    [SP + "test_certificate_expired_displayed_panel.py"],
)
T(
    "STRONG",
    "browser/components/safebrowsing/content/test/browser_bug400731.js; browser_bug415846.js; "
    "browser_whitelisted.js; browser_mixedcontent_aboutblocked.js",
    "The Safe Browsing interstitial for phishing and malware URLs, its detail panel and the "
    "allow-list path.",
    [SP + "test_phishing_and_malware_warnings.py"],
)
T(
    "STRONG",
    "browser/base/content/test/contextMenu/browser_strip_on_share_link.js; "
    "browser_strip_on_share_nested_link.js",
    "Copy Clean Link is exactly what the strip-on-share tests assert, including the nested-URL "
    "case.",
    [SP + "test_copy_clean_link.py"],
)
T(
    "STRONG",
    SID + "browser_identityPopup_clearSiteData.js; "
    "browser_identityPopup_clearSiteData_privateBrowsingMode.js; "
    "browser_identityPopup_clearSiteData_extensions.js",
    "Three tests for clearing cookies and site data from the identity panel.",
    [SP + "test_clear_cookies_site_data_via_panel.py"],
)

# ================================================================ private browsing
T(
    "STRONG",
    PBM
    + "browser_privatebrowsing_cleanup.js; browser_privatebrowsing_lastpbcontextexited.js; "
    "browser_privatebrowsing_last_private_browsing_context_exited.js; "
    "browser_privatebrowsing_localStorage_before_after.js",
    "The cleanup tests assert cookies and storage written in a private session are gone once "
    "the last private context exits.",
    [SP + "test_cookies_not_saved_private_browsing.py"],
)
T(
    "STRONG",
    PBM + "browser_privatebrowsing_cache.js",
    "A test dedicated to nothing being written to the HTTP cache from a private session.",
    [SP + "test_no_cached_file_in_private_browsing.py"],
)
T(
    "STRONG",
    PBM + "browser_privatebrowsing_placestitle.js; "
    "browser_privatebrowsing_placesTitleNoUpdate.js; browser_privatebrowsing_favicon.js; "
    "browser_privatebrowsing_history_shift_click.js",
    "The places tests assert a private visit is not recorded, which is what both the history "
    "and the address-bar exclusion tests check.",
    [
        SP + "test_private_session_history_exclusion.py",
        SP + "test_private_session_awesome_bar_exclusion.py",
    ],
)
T(
    "STRONG",
    PBM
    + "browser_privatebrowsing_ui.js; browser_privatebrowsing_context_and_chromeFlags.js; "
    "browser_privatebrowsing_windowtitle.js",
    "Opening a private window and the resulting window state, chrome flags and title are "
    "covered; the keyboard shortcut and the app-menu item are the two command paths these tests "
    "invoke.",
    [
        SP + "test_open_private_browsing_via_keyboard.py",
        SP + "test_private_window_from_panelui.py",
    ],
)
T(
    "STRONG",
    "browser/base/content/test/contextMenu/browser_contextmenu.js; "
    + PBM
    + "browser_privatebrowsing_ui.js; browser_privatebrowsing_newtab_from_popup.js",
    "browser_contextmenu.js asserts 'Open Link in New Private Window' is present on a link and "
    "the privatebrowsing tests cover the window it produces.",
    [SP + "test_open_link_in_private_window.py"],
)
T(
    "STRONG",
    "dom/security/test/https-first/browser_httpsfirst.js; "
    "browser_httpsfirst_console_logging.js; "
    + SID
    + "browser_identityPopup_HttpsOnlyMode.js",
    "browser_httpsfirst.js covers the scheme-less upgrade in private browsing, which is what "
    "both of these assert.",
    [
        SP + "test_https_enabled_private_browsing.py",
        SP + "test_https_first_mode_enabled_in_private_browsing_without_protocol.py",
    ],
)
T(
    "STRONG",
    PUI + "browser_protectionsUI_pbmode_exceptions.js; browser_protectionsUI_state.js",
    "Third-party tracking content being blocked in a private window is covered by the "
    "private-mode protections test.",
    [SP + "test_third_party_content_blocked_private_browsing.py"],
)
T(
    "STRONG",
    PBM + "browser_privatebrowsing_crh.js; "
    "browser/components/preferences/tests/privacy/browser_privacy_history_search_l10n_ids.js",
    "browser_privatebrowsing_crh.js drives the 'Never remember history' mode and asserts the "
    "resulting always-private behaviour.",
    [SP + "test_never_remember_browsing_history.py"],
)

# ================================================================ end private session (reset PBM)
T(
    "STRONG",
    PBM + "browser_privatebrowsing_resetPBM.js",
    "test_toolbar_button_visibility covers the button being present and removable, and "
    "test_reset_action_closes_sidebar the sidebar teardown -- both named assertions in the one "
    "test file dedicated to this feature.",
    [
        SP + "test_end_private_session_button_can_be_removed_or_added_on_toolbar.py",
        SP + "test_sidebar_removed_on_end_private_session.py",
    ],
)
T(
    "STRONG",
    PBM + "browser_privatebrowsing_resetPBM.js; browser_privatebrowsing_cleanup.js; "
    "browser_privatebrowsing_cache.js",
    "test_reset_action and test_reset_action_purges_session_store assert the session data is "
    "cleared by the reset, with the cleanup and cache tests covering what 'cleared' means for "
    "cookies and the cache.",
    [
        SP + "test_cache_is_cleared_via_end_private_session_button.py",
        SP + "test_end_private_session_clears_cookies.py",
    ],
)

# ================================================================ partial
T(
    "PARTIAL",
    PBM + "browser_privatebrowsing_resetPBM.js",
    "test_panel covers the confirmation panel, but no in-tree test cancels the reset from it "
    "and asserts the data survived -- the negative path this STARfox test owns.",
    [SP + "test_data_clearance_from_private_window_can_be_canceled.py"],
)
T(
    "PARTIAL",
    PBM + "browser_privatebrowsing_resetPBM.js; "
    "browser/components/downloads/test/browser/browser_about_downloads.js",
    "test_reset_action_purges_session_store covers the session-store purge, but the downloads "
    "list specifically is not re-checked after a reset.",
    [SP + "test_download_list_cleared_by_end_private_session.py"],
)
T(
    "PARTIAL",
    PBM + "browser_privatebrowsing_downloadLastDir.js; "
    "browser_privatebrowsing_downloadLastDir_toggle.js",
    "The in-tree private-browsing download tests are about the remembered download directory, "
    "not about whether a private download leaks into the normal-session download list.",
    [SP + "test_downloads_from_private_not_leaked.py"],
)
T(
    "PARTIAL",
    PBM + "browser_privatebrowsing_ui.js; "
    "browser/components/places/tests/browser/browser_autoshow_bookmarks_toolbar.js",
    "Bookmarks written from a private window are expected to persist -- the tree covers the "
    "bookmark-write path and the toolbar's visibility rules separately, but not the "
    "private-window-to-normal-window round trip these two tests make.",
    [
        SP + "test_add_bookmark_via_private_browsing_visible_in_regular_browsing.py",
        SP + "test_bookmarks_removed_via_private_browsing.py",
        SP + "test_bookmarks_toolbar_present_in_private_browsing.py",
    ],
)
T(
    "PARTIAL",
    "browser/components/sessionstore/test/browser_undoCloseById.js; "
    + PBM
    + "browser_privatebrowsing_cleanup.js",
    "Undo-close-tab is well covered, but not with the private-window constraint that the "
    "restored tab must not leak into the normal session.",
    [SP + "test_undo_close_tab_private_browsing.py"],
)
T(
    "PARTIAL",
    "toolkit/components/passwordmgr/test/browser/browser_autocomplete_generated_password_private_window.js; "
    "browser_doorhanger_autofill_then_save_password.js; "
    "browser/components/aboutlogins/tests/browser/browser_openSite.js",
    "The doorhanger tests cover saving from the prompt, and one covers the private-window "
    "variant for generated passwords, but the STARfox pair walks through to about:logins to "
    "confirm what was and was not stored -- that end-to-end leg is not asserted in tree.",
    [
        SP + "test_private_browser_password_doorhanger.py",
        SP + "test_passwords_appear_in_firefox_lockwise.py",
    ],
)
