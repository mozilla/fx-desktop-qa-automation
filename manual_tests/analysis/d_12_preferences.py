from _ledger import C, CSEC

# ---------------------------------------------------------------- suite 2241
# "Preferences" (527 cases). Tree: browser/components/preferences/tests/ - ~250
# browser-chrome tests across 20 pane sub-directories (home/, privacy/, etp/, search/,
# searchResults/, permissions/, languages/, downloads/, applications/, credentials/,
# networking/, sync/, siteData/, security/, performance/, moreFromMozilla/, aiFeatures/,
# experimental_features/, telemetry/). Behaviourally this is the best-covered pane set in
# the tree; what it never asserts is Figma/design conformance, themes, HCM, RTL, HiDPI,
# screen readers and window-resize layout - which is most of this suite's redesign sections.

# --- General pane (section 33976)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/browser_DefaultBrowserHelper.js; "
    "browser_defaultbrowser_alwayscheck.js; browser_browserIcon.js; browser_advanced_update.js; "
    "browser_updates_managed_by_os.js; "
    "browser/components/preferences/tests/home/browser_startup_browser_restore_session.js",
    "Setting Firefox as default browser, restoring windows/tabs from last time on launch, the "
    "version string, Check-for-updates, the three update-policy radio options and the update "
    "history list.",
    [143542, 143545, 143570, 143572, 143574, 143573, 143571],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/browser_tabs_browsing_pane.js; "
    "browser_tabs_open_external_next_to_active_tab.js; "
    "browser/components/tabbrowser/test/browser/tabs/browser_ctrlTab.js; browser_openURI_background.js",
    "Ctrl+Tab in recently-used order, links opening in tabs instead of windows, and switching "
    "immediately to a link opened in a new tab.",
    [143549, 143550, 161471],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/browser_build_font_options_test.js; browser_fluent.js; "
    "browser/components/preferences/tests/languages/browser_languages_pane.js; "
    "browser_browser_languages_preferred.js; browser_browser_languages_fallback.js; "
    "browser_website_language_reorder.js; browser_languages_subdialog.js; "
    "browser/components/preferences/tests/browser_checkspelling.js",
    "Default font and size, allowing pages to choose their own fonts, the preferred-languages "
    "list for pages, changing the browser language, and the spell-check toggle.",
    [143553, 143554, 143559, 143563, 143564, 178960, 145063, 250019, 250121,
     1771617, 1771618, 1771619],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/downloads/browser_downloads.js; "
    "browser_bug1547020_lockedDownloadDir.js; "
    "browser/components/preferences/tests/applications/browser_applications_selection.js; "
    "browser_change_app_handler.js; browser_filetype_dialog.js; browser_pdf_disabled.js",
    "Customising the download location and choosing how Firefox handles each downloaded file "
    "type / application, plus the DRM toggle.",
    [143567, 143568, 143569],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/browser_accessibility_pane.js; browser_accessibility_zoom.js; "
    "browser_colors_dialog.js",
    "Autoscrolling, smooth scrolling, caret browsing ('always use the cursor keys'), and "
    "search-for-text-when-you-start-typing.",
    [143581, 143582, 143584, 143586],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/searchResults/browser_search_within_preferences_1.js; "
    "browser_search_within_preferences_2.js; browser_search_within_preferences_command.js; "
    "browser_search_results.js; browser_search_no_results_change_category.js; browser_search_category_filter.js; "
    "browser_search_tooltip_position.js; browser_search_tooltip_moz_select.js; browser_search_overlapping_ranges.js; "
    "browser_search_results_back_button.js; browser_search_history_restoration.js; "
    "browser/components/preferences/tests/browser_bug1018066_resetScrollPosition.js; "
    "browser_bug1184989_prevent_scrolling_when_preferences_flipped.js; browser_setting_pane_scroll_restoration.js",
    "Search-within-preferences: result highlighting, tooltips on matched controls, clearing the "
    "search when a category is clicked, the no-results message, and the scroll/jump behaviour.",
    [145507, 145724, 145062, 145065, 145690, 145723, 249027, 3379377, 3392512, 3392513,
     3371655, 3371677, 3993275, 3381420, 3381421, 3372851, 3898271, 3898693],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/browser_keyboardfocus.js; browser_setting_pane_focus_restoration.js; "
    "browser_sub_pane_navigation_selection.js; browser_setting_pane_sub_pane.js; "
    "browser_setting_pane_sub_pane_search.js; browser_about_settings.js; browser_subdialogs.js; "
    "browser_legacy_pane_mappings.js",
    "Category navigation and sub-pane navigation in about:settings, focus restoration and "
    "sub-dialog handling.",
    [3381489, 3381490],
)
# --- Home pane (sections 33978, 861761)
CSEC(
    2241,
    "STRONG",
    "browser/components/preferences/tests/home/browser_homepage_homepage.js; browser_homepage_default.js; "
    "browser_homepage_custom_homepage_add_urls.js; browser_homepage_custom_homepage_add_multiple_urls.js; "
    "browser_homepage_custom_homepage_manage_urls.js; browser_homepage_custom_homepage_current_pages.js; "
    "browser_homepage_custom_homepage_bookmark.js; browser_homepage_custom_homepage_empty_state.js; "
    "browser_homepage_homepage_restore_defaults.js; browser_homepage_firefox_home.js; "
    "browser_homepage_firefox_home_disabled_both_off.js; browser_homepage_firefox_home_disabled_tabs_on.js; "
    "browser_homepage_firefox_home_disabled_windows_on.js; browser_hometab_restore_defaults.js; "
    "browser_newtab_menu.js; browser_homepages_use_bookmark.js",
    "The Home pane: homepage on launch, custom homepages (add, reorder, delete, from current "
    "pages, from bookmarks), blank page, restore-defaults, Firefox Home vs blank in new tabs, "
    "and the Firefox Home content toggles.",
    [33978],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/home/browser_homepage_firefox_home_shortcuts.js; "
    "browser_homepage_firefox_home_sponsored_shortcuts.js; browser_homepage_firefox_home_stories.js; "
    "browser_homepage_firefox_home_stories_personalization.js; browser_homepage_firefox_home_sponsored_stories.js; "
    "browser_homepage_firefox_home_manage_topics_opens_in_tab.js; "
    "browser_homepage_firefox_home_manage_topics_opens_in_window.js; "
    "browser_homepage_firefox_home_choose_wallpaper_opens_in_tab.js; "
    "browser_homepage_firefox_home_choose_wallpaper_opens_in_window.js; "
    "browser_homepage_firefox_home_recent_activity.js; browser_homepage_firefox_home_support_firefox.js; "
    "browser_homepage_firefox_home_widgets.js; browser_homepage_firefox_home_firefox_logo.js; "
    "browser_homepage_homepage_custom_homepage_button.js; browser_home_pane_late_group_registration.js; "
    "browser_homepage_custom_homepage_policy.js",
    "The redesigned Home & Startup page: default-browser section, startup section, custom-URL "
    "homepage (incl. reorder and delete), restore-defaults, and Firefox Home content - Shortcuts, "
    "Stories, Manage topics, Support Firefox, Recent activity and Choose wallpaper - each with a "
    "dedicated in-tree test.",
    [3898676, 3898677, 3898678, 3898679, 3898703, 3898704, 3898680, 3898681, 3898683,
     3898684, 3898685, 3898686, 3898687, 3898688, 3898689, 3898690, 3898702, 3898698],
)
# --- Search pane (sections 33979, 933974, 933975)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/search/browser_searchRestoreDefaults.js; "
    "browser_searchDefaultEngine.js; browser_searchChangedEngine.js; browser_search_engineList.js; "
    "browser_search_engine_reorder.js; browser_search_userEngineDialog.js; browser_localSearchShortcuts.js; "
    "browser_searchsuggestions.js; browser_searchShowSuggestionsFirst.js; browser_trendingsuggestions.js; "
    "browser_search_firefoxSuggest.js; browser_searchFindMoreLink.js; browser_searchScroll.js",
    "The Search pane: restore default engines, the default-engine dropdown (normal and private "
    "window), adding an engine, reordering engines, editing an installed engine (keyword), and "
    "enabling/disabling engines from the keyboard.",
    [143596, 145302, 4105787, 4105788, 4105790, 4105791, 4105792, 4105793],
)
# --- Privacy pane (sections 33980, 933948)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/privacy/browser_privacypane_2.js; browser_privacypane_3.js; "
    "browser_warning_permanent_private_browsing.js; browser_sanitizeOnShutdown_prefLocked.js; "
    "browser_shutdownClearingExceptions.js; "
    "browser/components/preferences/tests/siteData/browser_siteData.js; browser_siteData2.js; "
    "browser_siteData3.js; browser_siteData_multi_select.js; browser_siteData_search.js; "
    "browser_clearSiteData_v2.js; "
    "browser/components/preferences/tests/etp/browser_cookies_exceptions.js; "
    "browser_cookie_exceptions_addRemove.js; "
    "browser/base/content/test/sanitize/browser_sanitizeDialog_v2.js; "
    "browser/components/preferences/tests/security/browser_security-1.js; browser_security-2.js; "
    "browser_security-3.js",
    "History mode (never remember / custom / always private / remember), clear-on-exit "
    "customisation, the Clear Recent History panel, total cookie+cache usage, the Clear Data and "
    "Manage Cookies and Site Data panels, session-only cookies, third-party cookie blocking, and "
    "the three Safe Browsing checkboxes.",
    [143604, 143605, 143606, 143608, 143610, 143611, 143618, 143627, 143633, 143634,
     159261, 159391, 159455, 145294, 145301, 249028,
     143603, 4105694, 143636, 4105695, 4105697, 4105669, 4108601, 143653, 143655],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/etp/browser_contentblocking.js; browser_contentblocking_categories.js; "
    "browser_etp_customize_1.js; browser_etp_customize_2.js; browser_etp_customize_3.js; browser_etp_customize_4.js; "
    "browser_etp_advanced.js; browser_etp_status.js; browser_etp_exceptions_dialog.js; "
    "browser_contentblocking_standard_tcp_section.js; browser_statePartitioning_strings.js",
    "The ETP settings panel: Standard/Strict/Custom, the advanced settings menu, the status card "
    "and the exceptions dialog.",
    [3347220, 3347215, 3347216, 3347217, 4105797, 3347228, 3347229],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/privacy/browser_privacy_dnsoverhttps.js; "
    "browser_privacy_dnsoverhttps_srd.js; "
    "browser/components/preferences/tests/networking/browser_dns_over_https_exceptions_subdialog.js",
    "The DNS over HTTPS panel and its exceptions sub-dialog.",
    [3347231],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/networking/browser_connection.js; browser_connection_bug1445991.js; "
    "browser_connection_bug1505330.js; browser_connection_bug388287.js; browser_connection_valid_hostname.js; "
    "browser_connection_system_wpad.js; browser_proxy_backup.js; browser_connection_telemetry.js",
    "The Connections / proxy panel and its advanced settings.",
    [3349337, 3349338],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/privacy/browser_privacypane_3.js; "
    "browser/base/content/test/sanitize/browser_sanitize-history.js; browser_sanitize-timespans.js",
    "The History panel: options, functionality and the customise-history sub-menu.",
    [3347225, 3347226, 3347227],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/siteData/browser_clearSiteData_v2.js; browser_siteData_search.js; "
    "browser_siteData_multi_select.js; browser/base/content/test/sanitize/browser_sanitizeDialog_v2.js; "
    "browser/components/preferences/tests/etp/browser_cookie_exceptions_addRemove.js",
    "The Browsing data panel: clear-browsing-data, clear-data-for-specific-websites, manage "
    "exceptions and the clear-cookies checkbox.",
    [3347219, 3347221, 3347222, 3347223, 3347224],
)
# --- Permissions (sections 700154, 934331)
CSEC(
    2241,
    "STRONG",
    "browser/components/preferences/tests/permissions/browser_permissions_dialog.js; "
    "browser_permissions_dialog_default_perm.js; browser_permissions_checkPermissionsWereAdded.js; "
    "browser_capability_filter.js; browser_permissions_about_hidden.js; browser_permissions_urlFieldHidden.js; "
    "browser_notifications_do_not_disturb.js; browser_pip_settings.js",
    "Per-permission settings dialogs (location, camera, microphone, notifications, autoplay) - "
    "setting, changing and removing an entry - and the pop-up blocker checkbox.",
    [934331],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/permissions/browser_permissions_dialog.js; "
    "browser_capability_filter.js; browser_pip_settings.js; browser_notifications_do_not_disturb.js; "
    "browser/components/preferences/tests/privacy/browser_privacy_uploadEnabled.js; "
    "browser_privacy_segmentation_pref.js; browser/components/preferences/tests/browser_extension_controlled.js",
    "The Permissions rows in the redesigned Privacy page (location, camera, microphone, speaker, "
    "notifications, autoplay, VR, pop-up blocking, manage-redirects, extension-install warning and "
    "allow-list) and the Firefox Data Collection and Use controls.",
    [3350665, 3350666, 3350667, 3350668, 3350669, 3350670, 3350671, 3350672, 3350673,
     3350674, 3350676, 3381409, 3381413, 3381496],
)
# --- Appearance / accessibility panes (700149, 707339-707343)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/browser_appearance_pane.js; browser_browserIcon.js; "
    "browser/components/sidebar/tests/browser/browser_customize_sidebar.js; browser_vertical_tabs.js",
    "The Appearance page: changing the website-appearance theme, 'Manage Firefox themes' opening "
    "about:addons, changing the browser layout, the show-sidebar toggle, and the two cross-links "
    "into Accessibility and Home settings.",
    [3374385, 3374405, 3374409, 3374410, 3374411, 3374412, 3374413],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/browser_accessibility_zoom.js",
    "The Default zoom section: the dropdown level being applied, 'Zoom text only', and "
    "Restore defaults.",
    [3369710, 3369712, 3369716, 3369718],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/browser_build_font_options_test.js; browser_fluent.js",
    "The Fonts section: font family, size, the Advanced fonts dialog and Restore defaults.",
    [3369891, 3370446, 3370695, 3370696, 3370698],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/browser_colors_dialog.js",
    "Website contrast / Override colors set to Off, Custom and Automatic, plus Restore defaults.",
    [3371314, 3371437, 3371664, 3371685, 3371695],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/browser_accessibility_pane.js",
    "The Keyboard navigation and scrolling section: Tab-key focus behaviour, auto scrolling, "
    "smooth scrolling and always-underline-links.",
    [3371744, 3371846, 3371847, 3371848, 3371849, 3371853, 3371854, 3372695],
)
# --- Downloads / Applications settings page (700150)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/downloads/browser_downloads.js; "
    "browser_downloads_handle_new_file_types.js; browser_open_download_preferences.js; "
    "browser_bug1547020_lockedDownloadDir.js; "
    "browser/components/preferences/tests/applications/browser_applications_selection.js; "
    "browser_applications_filter.js; browser_applications_search_results.js; browser_change_app_handler.js; "
    "browser_filetype_dialog.js; browser_application_xml_handle_internally.js; browser_pdf_disabled.js",
    "The Downloads settings page: changing the folder (and its telemetry), 'Always ask where to "
    "save files' on and off, delete-files-downloaded-in-private-browsing, every Applications "
    "dropdown (AVIF, XML, mailto, PDF, SVG, WebP), the 'what to do with other files' default, "
    "adding new content types, and searching file types.",
    [3374387, 3374388, 3374389, 3374390, 3374391, 3374396, 3379188, 3379189, 3379205,
     3379206, 3392470, 3392474, 3392475, 3379944, 3392515, 3379945, 3379946, 3381412,
     3379947],
)
# --- Languages / Translations page (700153)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/languages/browser_languages_pane.js; "
    "browser_browser_languages_preferred.js; browser_browser_languages_preferred_remote.js; "
    "browser_browser_languages_fallback.js; browser_browser_languages_subdialog.js; "
    "browser_languages_subdialog.js; browser_website_language_reorder.js",
    "The Languages page: adding / changing / deleting a preferred language, the fallback-language "
    "list and its fallback behaviour when localisation is incomplete, and adding, reordering and "
    "deleting website languages.",
    [3399148, 3399149, 3399150, 3399151, 3399152, 3399153, 3399154, 3399155, 3399156,
     3399157, 3399158, 3399159, 3987581],
)
C(
    2241,
    "STRONG",
    "browser/components/translations/tests/browser/browser_translations_about_preferences_manage_downloaded_languages.js; "
    "browser_translations_about_settings_main_page_offer_checkbox.js; "
    "browser_translations_about_settings_subpage_always_translate_langs_basic.js; "
    "browser_translations_about_settings_subpage_always_translate_langs_modify.js; "
    "browser_translations_about_settings_subpage_never_translate_langs_basic.js; "
    "browser_translations_about_settings_subpage_never_translate_langs_modify.js; "
    "browser_translations_about_settings_subpage_never_translate_sites_basic.js; "
    "browser_translations_about_settings_subpage_download_langs_basic.js; "
    "browser_translations_about_settings_subpage_download_langs_errors.js; "
    "browser_translations_about_settings_subpage_download_langs_delete_confirmation.js; "
    "browser_translations_full_page_panel_basics.js; "
    "toolkit/components/translations/tests/browser/browser_about_translations_enabling.js",
    "The translation settings: 'Offer full page translation' on and off, the always-translate and "
    "never-translate language lists, the never-translate sites list, and the Speed-up-translation "
    "language downloads including the delete / cancel / error / retry states.",
    [3399160, 3399161, 3399162, 3399163, 3399165, 3399166, 3399168, 3399170, 3399171,
     3399172, 3399173, 3399174, 3399175, 3399176, 3399177, 3399534],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/browser_checkspelling.js; "
    "browser/components/preferences/tests/languages/browser_languages_pane.js",
    "Spell-check dictionaries: downloading them and the checker recognising existing ones.",
    [3987577, 3987578, 3987579],
)
# --- About Firefox / More from Mozilla (700156, 700157, 700159)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/browser_advanced_update.js; browser_updates_managed_by_os.js; "
    "browser/components/preferences/tests/telemetry/browser_usage_telemetry_support_link.js",
    "The About Firefox card: Check for updates, What's new, Show update history, the three update "
    "policy options, and the Get help / Share ideas links.",
    [3374337, 3374338, 3374339, 3374340, 3374342, 3374343, 3374344, 3374345, 3391732,
     3898900, 3898901, 3898902, 3898903],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/moreFromMozilla/browser_moreFromMozilla.js; "
    "browser_moreFromMozilla_config.js; browser_moreFromMozilla_locales.js; browser_moreFromMozilla_monitor.js; "
    "browser_moreFromMozilla_relay.js; browser_moreFromMozilla_vpn.js; browser_moreFromMozilla_utm_srd.js",
    "The More from Mozilla page: each product card's presence, strings and link/UTM target, "
    "including the mobile QR and email-the-link actions.",
    [3376248, 3375213, 3376342, 3375054, 3375214, 3375725, 3375728, 3375730, 3375732,
     3375734, 3376246, 3379383],
)
# --- Tabs and browsing page (707941, 707942)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/browser_tabs_browsing_pane.js; "
    "browser_tabs_open_external_next_to_active_tab.js; "
    "browser/components/preferences/tests/performance/browser_performance.js; browser_layersacceleration.js; "
    "browser/components/preferences/tests/privacy/browser_containers_dialog_size.js; browser_containers_name_input.js; "
    "browser/components/preferences/tests/permissions/browser_pip_settings.js; "
    "browser/components/tabbrowser/test/browser/tabs/browser_ctrlTab.js; browser_tab_preview.js; "
    "browser/components/sidebar/tests/browser/browser_customize_sidebar.js; browser_vertical_tabs.js; "
    "toolkit/components/pictureinpicture/tests/",
    "The Tabs and browsing page controls: tab layout, sidebar on/off, tab settings, focus new tab "
    "immediately, Ctrl+Tab cycling, tab hover preview, AI tab suggestions, containers (default "
    "on/off, add/remove, extension-controlled), close-multiple-tabs and quit warnings, caret "
    "browsing, find-as-you-type, Picture-in-Picture on/off and across tab switches, DRM, the "
    "performance settings and the recommendations settings.",
    [3371694, 4045973, 3371704, 3371705, 3371706, 3371707,
     4045974, 4045975, 3372978, 3372979, 3372993, 3372994, 3372996, 3372998, 3372999,
     3373000, 3373002, 3373004, 3373008, 3373010, 3373013, 3373014, 3373015, 3373017,
     3373020, 3381507, 3908597, 3380003, 3381514],
)
# --- Account and sync page (707956-707967)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/sync/browser_sync_settings_ui.js; browser_sync_chooseWhatToSync.js; "
    "browser_sync_disabled.js; browser_account_sync_visibility.js; browser_sync_pairing.js; "
    "browser/components/preferences/tests/browser_open_migration_wizard.js; "
    "browser/components/preferences/tests/browser_backup_visibility.js; browser_backup_warning_banner.js; "
    "browser/components/profiles/tests/browser/browser_preferences.js; "
    "browser/components/preferences/tests/browser_DefaultBrowserHelper.js",
    "The Account and sync page: the account and sync sections signed out and signed in, "
    "choose-what-to-sync, the Import browser data section and its wizard, the Profile section, the "
    "Backup/Restore sections and their visibility, and the default-browser section.",
    [3371620, 3371621, 3372854, 3372858, 3372860, 3372866, 3372868, 3371735, 3371981,
     3371982, 3371983, 3371984, 3372821, 3897443],
)
# --- Passwords & Autofill settings page (861687-861699, 938688)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/credentials/browser_password_management.js; "
    "browser_primaryPassword.js; browser_site_login_exceptions.js; browser_site_login_exceptions_policy.js; "
    "browser_cert_export.js; "
    "browser/components/preferences/tests/privacy/browser_privacy_passwordGenerationAndAutofill.js; "
    "browser/components/aboutlogins/tests/browser/browser_osAuthDialog.js; "
    "browser/components/preferences/tests/browser_privacy_trustPanelBreachAlerts.js",
    "The Passwords section of the redesigned settings page: 'Ask to save passwords' on/off, "
    "'Require device sign in to manage passwords' (OS auth), setting / changing / rejecting / "
    "cancelling / removing a Primary Password, the breached-website alerts checkbox, the "
    "exceptions dialog (add, remove, cancel), 'Manage saved passwords' opening about:logins, and "
    "disabling autofill + strong-password suggestions.",
    [3898126, 3898127, 3898128, 3898130, 3898131, 3898133, 3898134, 3898136, 3898138,
     3898139, 143598, 148408, 143600],
)
C(
    2241,
    "STRONG",
    "browser/extensions/formautofill/test/browser/creditCard/browser_editCreditCardDialog.js; "
    "browser/extensions/formautofill/test/browser/browser_editAddressDialog.js; browser_manageAddressesDialog.js; "
    "browser/extensions/formautofill/test/browser/address/browser_manageAddressesSubpage.js; "
    "browser/extensions/formautofill/test/browser/browser_privacyPreferences.js; "
    "browser/extensions/formautofill/test/browser/creditCard/browser_creditCard_osAuth.js",
    "The Payment methods and Addresses sections: adding, editing and deleting a card or an "
    "address, the save-and-autofill toggles and the OS-auth toggle.",
    [3898157, 3898161, 3898162, 3898172, 3898176],
)
C(
    2241,
    "STRONG",
    "browser/components/preferences/tests/credentials/browser_site_login_exceptions_policy.js; "
    "browser_site_login_exceptions_policy_xul.js; browser/components/enterprisepolicies/tests/browser/",
    "The password/autofill enterprise policies (autofilladdressenabled, autofillcreditcardenabled, "
    "offertosavelogins(+default), passwordmanagerenabled, PasswordManagerExceptions, "
    "primarypassword, disablemasterpasswordcreation, DisablePasswordReveal).",
    [3898299, 3898300, 3898301, 3898302, 3898303, 3898304, 3898305, 3898306, 3898307],
)
C(
    2241,
    "MEDIUM",
    "browser/components/preferences/tests/browser_about_settings.js; browser_appearance_pane.js; "
    "browser_setting_group_in_progress.js; browser_spotlight.js",
    "Everything design/Figma-conformance, theme, High Contrast, RTL, HiDPI, screen-reader, "
    "window-resize, zoom-level, text-selection/drag-drop, offline-mode and post-crash / "
    "post-upgrade persistence in the redesigned Settings sections. browser-chrome asserts control "
    "behaviour, never appearance, so these have no in-tree counterpart.",
    [3347233, 3350663, 3372845, 3372846, 3376440, 3376441, 3376442, 3381472,
     3374386, 3379187, 3374392, 3374393, 3374394, 3374395, 3379948, 3381423, 3392479,
     3381426, 3392489, 3381414, 3965985,
     3371512, 3371517, 3371540, 3371516,
     3399139, 3399144, 3399147, 3399178, 3399179, 3399180, 3399181, 3399182, 3399183,
     3399184, 3987580, 3987582, 4056099,
     3351416, 3351412, 3351421, 3351422, 3351414, 3351415, 3379375, 3379376, 3379379,
     3379378, 3379380, 3379381, 3351417, 3351418, 3351419, 3351420, 3379369, 3379371,
     3379373, 3379374, 3381476,
     3373019, 3374341, 3374346, 3374347, 3374348, 3374349, 3898899,
     3375053, 3379399, 3993274, 3379400, 3379401, 3931200,
     3350675, 3350705, 3350706, 3350707, 3350709, 3350710, 3350711,
     3371622, 3371652, 3371654, 3371656, 3371657, 3371663, 3371678, 3371679, 3371693,
     4045554, 3371606, 3371608, 3371609, 3371610, 3371611,
     3373022, 3379372, 3381508, 3381509, 3381513, 3392517, 3379943, 3379382,
     3371623, 3371630, 3371628, 3371651, 3381407, 3896867, 3896868, 3371681, 3371703,
     3371762, 3372632,
     3372849, 3372850, 3372852, 3372853, 3372855, 3372856,
     3374401, 3374402, 3381424, 3374403,
     3898268, 3898269, 3898270, 3898272, 3898273, 3898274, 3898275, 3898276, 3898277,
     3898278, 3898279, 3898280, 3898281, 3898282, 3898283, 3898284, 3898285, 3898286,
     3898125, 3898142, 3898156, 3898171, 3898178, 3898314,
     3898247, 3898248, 3898249, 3898250, 3898251, 3898252, 3898253,
     3898254, 3898255, 3898256, 3898257, 3898258, 3898259,
     3898261, 3898262, 3898263, 3898264, 3898265, 3898266,
     3898682, 3898691, 3898692, 3898694, 3898695, 3898696, 3898697, 3898699, 3898700,
     3898701, 3898669, 3898670, 3898671, 3898672, 3898673,
     3399185, 3399186, 3399187, 3399188, 3399189, 3399190, 3399191, 3399192, 3399193,
     143552, 1344007, 145230, 167989, 159150,
     3991915, 3991916, 4060271, 4060272, 3371851, 3371852],
)
