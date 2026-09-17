from _ledger import C, CSEC

# ---------------------------------------------------------------- suite 5833
# "Security and Privacy" (354 cases). Tree: browser/base/content/test/protectionsUI/ (25),
# .../siteIdentity/ (37), browser/components/urlbar/tests/browser-trustPanel/ (6),
# browser/components/protections/test/browser/ (7),
# browser/components/privatebrowsing/test/browser/ (46),
# toolkit/components/antitracking/test/browser/ (126),
# dom/security/test/https-first|https-only/, toolkit/components/httpsonlyerror/tests/browser/ (6),
# browser/components/safebrowsing/content/test/ (4).
#
# NOTE: ~70 cases in this suite (sections 58679, 58863-58866) test the *Firefox Monitor
# website* and its Bento menu, and ~18 (58683) test Windows Family Safety. Neither is
# Firefox-desktop code; there is nothing in the tree to compare them to.

C(
    5833,
    "STRONG",
    "browser/base/content/test/protectionsUI/browser_protectionsUI.js; browser_protectionsUI_categories.js; "
    "browser_protectionsUI_state.js; browser_protectionsUI_state_reset.js; browser_protectionsUI_icon_state.js; "
    "browser_protectionsUI_shield_visibility.js; browser_protectionsUI_pbmode_exceptions.js; "
    "browser_protectionsUI_open_preferences.js; browser_protectionsUI_background_tabs.js",
    "The ETP defaults (Standard on, in normal and private windows), turning protection on/off per "
    "site, exception handling (remembered in normal browsing, not in PBM), the Custom mode's "
    "effect on private vs normal windows, and the shield/icon states.",
    [446321, 446322, 103329, 103330, 107718, 107717, 446323, 446324, 446325, 446319,
     446318, 448321, 1017505],
)
C(
    5833,
    "STRONG",
    "browser/base/content/test/protectionsUI/browser_protectionsUI_cryptominers.js; "
    "browser_protectionsUI_fingerprinters.js; browser_protectionsUI_socialtracking.js; "
    "browser_protectionsUI_trackers_subview.js; browser_protectionsUI_tracker_cookies_subview.js; "
    "browser_protectionsUI_cookies_subview.js; browser_protectionsUI_email_trackers_subview.js; "
    "browser_protectionsUI_suspicious_fingerprinters_subview.js; browser_protectionsUI_fetch.js",
    "Each tracker category being blocked and listed in the protections panel and its subviews: "
    "cryptominers, fingerprinters (incl. suspected), social trackers, cross-site tracking cookies "
    "and email trackers - in Standard and Strict.",
    [450231, 450232, 450233, 450234, 387362, 387363, 387364, 387365,
     2272188, 2268774, 2273349, 2318651, 2318652, 2318653,
     2119673, 2091280, 2089250, 3956],
)
C(
    5833,
    "STRONG",
    "browser/components/protections/test/browser/browser_protections_report_ui.js; browser_protections_lockwise.js; "
    "browser_protections_monitor.js; browser_protections_telemetry.js; browser_privacy_metrics_card.js; "
    "browser_privacyMetrics_actor.js",
    "about:protections: the per-category blocked counts, the graph, the Lockwise/passwords card "
    "and its link, and the redirect to about:preferences#privacy.",
    [448309, 448310, 448311, 448312, 448313, 448314, 448316, 448317, 448318, 448319,
     448325, 448326, 448327],
)
C(
    5833,
    "STRONG",
    "browser/base/content/test/protectionsUI/browser_protectionsUI_telemetry.js",
    "ETP panel telemetry.",
    [3058456],
)
C(
    5833,
    "STRONG",
    "browser/components/urlbar/tests/browser-trustPanel/browser_trust_panel.js; browser_trust_panel_icon.js; "
    "browser_trust_panel_pages.js; browser_trust_panel_security_view.js; browser_trust_panel_cert_exception.js; "
    "browser_trust_panel_focus.js; browser/base/content/test/popupNotifications/"
    "browser_popupNotification_hide_after_trust_panel.js",
    "The unified Trust Panel: the icon state on safe / unsafe / still-tracking / ETP-off sites, "
    "the panel on insecure connections, after a bad-SSL exception, on the HTTP<->HTTPS switch, "
    "and the private-window variants.",
    [3056988, 3056989, 3056990, 3056991, 3057428, 3057429, 3057430, 3057718, 3057719,
     3061008, 3061009, 3061010],
)
C(
    5833,
    "STRONG",
    "browser/base/content/test/siteIdentity/browser_check_identity_state.js; browser_identity_UI.js; "
    "browser_identityPopup_focus.js; browser_identityBlock_focus.js; browser_identityPopup_custom_roots.js; "
    "browser_identityPopup_qwacs.js; browser_getSecurityInfo.js; browser_mixed_passive_content_indicator.js; "
    "browser_csp_block_all_mixedcontent.js; browser_mixed_content_cert_override.js; "
    "browser_mixed_content_with_navigation.js; browser_no_mcb_on_http_site.js; "
    "browser_secure_transport_insecure_scheme.js; browser_check_identity_state_pdf.js; "
    "browser/components/urlbar/tests/browser-trustPanel/browser_trust_panel_security_view.js",
    "The lock icon and connection text for HTTP / HTTPS / mixed content / DV / EV / expired "
    "certificate, the second-level 'Connection secure' view, and the View-certificate and "
    "More-information links.",
    [3054027, 3054028, 3054044, 3054043, 3054040, 3054041, 3054042, 3054045, 3054046,
     3054885, 3952],
)
C(
    5833,
    "STRONG",
    "browser/base/content/test/protectionsUI/browser_protectionsUI_trackers_subview.js; "
    "browser_protectionsUI_tracker_cookies_subview.js; browser_protectionsUI_cookies_subview.js; "
    "browser_protectionsUI_cryptominers.js; browser_protectionsUI_fingerprinters.js; "
    "browser_protectionsUI_socialtracking.js; browser_protectionsUI_subview_shim.js; "
    "browser_protectionsUI_milestones.js; browser_protectionsUI_info_message.js; "
    "browser/base/content/test/siteIdentity/browser_identityPopup_clearSiteData.js",
    "The unified ETP panel body: tracker counts (and zero-tracker sites), each category subview "
    "in blocked and not-blocked states, 'See all', 'Clear cookies and site data', the "
    "'Privacy settings' footer link, the ETP toggle, and the first-run render.",
    [3054031, 3054032, 3054909, 3054910, 3054911, 3054912, 3054913, 3054917, 3054914,
     3054918, 3054916, 3054915, 3054033, 3054035, 3054036, 3054034, 3054904, 3054905,
     3054906, 3054907, 3054908, 3054026],
)
C(
    5833,
    "STRONG",
    "browser/base/content/test/siteIdentity/browser_deprecatedTLSVersions.js",
    "TLS 1.0 / 1.1 connections refused and TLS 1.2 accepted.",
    [3950, 3951, 192739],
)
C(
    5833,
    "STRONG",
    "browser/components/safebrowsing/content/test/browser_bug400731.js; browser_bug415846.js; "
    "browser_whitelisted.js; browser_mixedcontent_aboutblocked.js",
    "The Safe Browsing interstitial: shown for phishing/malware/unwanted, the 'ignore the warning' "
    "path, and the report-button visibility rules.",
    [3954, 3955, 50353, 50354, 50355],
)
CSEC(
    5833,
    "STRONG",
    "browser/components/aboutlogins/tests/browser/browser_breachAlertShowingForAddedLogin.js; "
    "browser_breachAlertLinkTelemetry.js; browser_alertDismissedAfterChangingPassword.js; "
    "browser_vulnerableLoginAddedInSecondaryWindow.js; browser_fxAccounts.js; browser_tabKeyNav.js; "
    "browser/components/preferences/tests/browser_privacy_trustPanelBreachAlerts.js",
    "The breached-login warning icon and Breach Dialog in about:logins: appearing for a login added "
    "directly or via the doorhanger, in a private window, the 'Learn more about this breach' link "
    "and its keyboard access, dismissal after a password change, persistence after a username "
    "change, and the post-Sync state.",
    [58641],
    exclude=[392794],  # dark/light theme rendering
)
# --- private browsing
C(
    5833,
    "STRONG",
    "browser/components/privatebrowsing/test/browser/browser_privatebrowsing_ui.js; "
    "browser_privatebrowsing_about.js; browser_privatebrowsing_context_and_chromeFlags.js; "
    "browser_privatebrowsing_windowtitle.js; browser_privatebrowsing_nonbrowser.js; "
    "browser_privatebrowsing_crh.js; browser_privatebrowsing_noSessionRestoreMenuOption.js; "
    "browser_privatebrowsing_indicator.js",
    "Opening a private window from the hamburger menu and by keyboard, opening a link in one, "
    "'always use private browsing mode', the permanent-PBM restrictions (custom history settings "
    "locked, undo-close-tab, add-ons manager) and the no-warning-on-close behaviour.",
    [101660, 101661, 101662, 104891, 118732, 118742, 118735, 105204, 118812],
)
CSEC(
    5833,
    "STRONG",
    "browser/components/privatebrowsing/test/browser/browser_privatebrowsing_placestitle.js; "
    "browser_privatebrowsing_placesTitleNoUpdate.js; browser_privatebrowsing_history_shift_click.js; "
    "browser_privatebrowsing_favicon.js; browser_privatebrowsing_urlbarfocus.js; "
    "browser_privatebrowsing_lastpbcontextexited.js; browser_privatebrowsing_last_private_browsing_context_exited.js",
    "Private-session visits absent from the History menu, the Library panel, the Library window "
    "and the urlbar list, and undo-close-tab inside a private window.",
    [59078],
    exclude=[120453, 120454, 120455, 101748, 107721],
)
CSEC(
    5833,
    "STRONG",
    "toolkit/components/passwordmgr/test/browser/browser_private_window.js; "
    "browser/components/aboutlogins/tests/browser/browser_primaryPassword.js",
    "No automatic save-password doorhanger in PBM, and setting/removing a Primary Password from a "
    "private window.",
    [59079],
)
C(
    5833,
    "STRONG",
    "uriloader/exthandler/tests/mochitest/browser_download_privatebrowsing.js; "
    "browser/components/privatebrowsing/test/browser/browser_privatebrowsing_downloadLastDir.js; "
    "browser_privatebrowsing_downloadLastDir_c.js; browser_privatebrowsing_downloadLastDir_toggle.js; "
    "browser_privatebrowsing_DownloadLastDirWithCPS.js",
    "Private-window downloads: saved to disk, not leaked into the normal-window download list, and "
    "the last-directory isolation.",
    [101674, 101676, 99156],
)
CSEC(
    5833,
    "STRONG",
    "browser/components/places/tests/browser/browser_bookmark_private_window.js",
    "Bookmarks created or removed in a private window are visible in normal sessions.",
    [59081],
    exclude=[101746],  # cross-browser import
)
CSEC(
    5833,
    "STRONG",
    "browser/components/privatebrowsing/test/browser/browser_privatebrowsing_cache.js; "
    "browser_privatebrowsing_localStorage.js; browser_privatebrowsing_localStorage_before_after.js; "
    "browser_privatebrowsing_cleanup.js; browser_privatebrowsing_concurrent.js; "
    "browser/components/places/tests/browser/browser_forgetthissite.js",
    "Private-session cache and cookies not persisting, and Forget-About-This-Site removing all "
    "cookies for the base domain.",
    [59082, 59083],
)
C(
    5833,
    "STRONG",
    "browser/components/privatebrowsing/test/browser/browser_privatebrowsing_resetPBM.js; "
    "browser_privatebrowsing_sidebar.js; browser_privatebrowsing_cleanup.js",
    "The 'clear private session data' toolbar button: the success notification, cancelling, "
    "adding/removing the button, the sidebar being reset, the downloads list emptied, and cookies "
    "and cache actually cleared.",
    [2359313, 2359314, 2359315, 2359316, 2359317, 2359319, 2359320],
)
# --- preferences-driven privacy
C(
    5833,
    "STRONG",
    "browser/components/preferences/tests/privacy/; browser/base/content/test/sanitize/browser_sanitizeDialog_v2.js; "
    "browser/base/content/test/sanitize/browser_sanitize-formhistory.js; browser_sanitize-history.js; "
    "browser_sanitize-cookie-exceptions.js; browser_cookiePermission.js",
    "The Privacy pane switches: never remember history, don't remember browsing/download history, "
    "don't remember search and form history, clear history on close, reject cookies / third-party "
    "cookies / delete-on-close, and 'Ask to save logins' off.",
    [102378, 102381, 105208, 105209, 107103, 446332, 446333, 446334],
)
# --- permissions
CSEC(
    5833,
    "STRONG",
    "browser/base/content/test/permissions/browser_permissions.js; browser_temporary_permissions.js; "
    "browser_temporary_permissions_api.js; browser_temporary_permissions_api_e2e.js; "
    "browser_temporary_permissions_navigation.js; browser_temporary_permissions_cross_origin_navigation.js; "
    "browser_temporary_permissions_tabs.js; browser_temporary_permissions_expiry.js; "
    "browser_permission_delegate_geo.js; browser_permissions_delegate_vibrate.js; "
    "browser_permissions_handling_user_input.js; browser_site_scoped_permissions.js; "
    "browser/base/content/test/webrtc/; browser/modules/test/browser/browser_SitePermissions.js; "
    "browser_SitePermissions_combinations.js",
    "Permission prompts for geolocation / audio / video / screen at top level and same origin, the "
    "blocked-permission icons, cross-origin iframes with and without the allow attribute, "
    "sandboxed iframes, always-denied permissions, and 'Remember this decision' for allow and deny "
    "including after in-iframe navigation.",
    [76676, 76677, 76679, 76680, 76681, 76682],
)
# --- HTTPS-First / HTTPS-Only
C(
    5833,
    "STRONG",
    "dom/security/test/https-first/browser_httpsfirst.js; browser_httpsfirst_console_logging.js; "
    "browser_httpsfirst_speculative_connect.js; dom/security/test/https-only/browser_httpsonly_prefs.js; "
    "browser/base/content/test/siteIdentity/browser_identityPopup_HttpsOnlyMode.js; "
    "toolkit/components/httpsonlyerror/tests/browser/browser_errorpage.js; browser_exception.js; "
    "browser_errorpage_www_suggestion.js; browser_errorpage_timeout.js",
    "HTTPS-First upgrading in private and normal browsing (with and without an explicit scheme), "
    "the console messages, the fallback to HTTP when HTTPS is unsupported, the Site Information "
    "panel state, and the three HTTPS-Only pref settings including per-site exceptions.",
    [1362731, 1362263, 1362264, 1362265, 1364743, 1364748, 1364409,
     1364750, 1364751, 1364752, 1364753, 1378884,
     1364754, 1364755, 1364756, 1378883],
)
C(
    5833,
    "STRONG",
    "browser/base/content/test/contextMenu/browser_strip_on_share_link.js; browser_strip_on_share_nested_link.js; "
    "browser/components/urlbar/tests/browser/browser_strip_on_share.js; browser_observers_for_strip_on_share.js; "
    "browser_strip_on_share_telemetry.js",
    "Query parameters stripped from a copied link.",
    [2307354],
)
C(
    5833,
    "MEDIUM",
    "toolkit/components/resistfingerprinting/tests/browser/; "
    "browser/components/resistfingerprinting/test/browser/ (50 tests); "
    "browser/components/privatebrowsing/test/browser/browser_privatebrowsing_theming.js; "
    "browser/base/content/test/protectionsUI/browser_protectionsUI_bounce_tracking_protection.js",
    "Fingerprinting-protection font/canvas behaviour is verified at unit/gtest altitude rather "
    "than through the ETP toggle. The remaining cases in this suite are the Firefox Monitor "
    "*website* (sections 58679, 58863-58866), Windows Family Safety (58683), Safe Browsing "
    "database/back-off internals, the Windows DLP agent, taskbar pinning, add-on interactions, "
    "and every HCM / RTL / screen-reader / theme / touchscreen variant - none of which the tree "
    "asserts.",
    [2230197, 2230213, 2250851, 2251461, 2318656, 2318657,
     1811749, 2071166, 3068453, 3073366,
     2359321, 2359322, 2359323, 2359324, 2317830,
     227180, 446331, 1122032, 448307,
     50351, 50357, 50358, 50359, 50360, 50361, 125325, 129941, 130438, 171423,
     247419, 294453,
     1371490, 1371491, 2153822],
)