from _ledger import C, CSEC

# ---------------------------------------------------------------- suite 43517
# "Password manager" (427 cases). Tree: toolkit/components/passwordmgr/test/browser/ (68),
# browser/components/aboutlogins/tests/browser/ (29),
# toolkit/components/satchel/megalist/content/tests/browser/ (13).

# --- autocomplete dropdown + context menu fill (sections 410253-410258)
C(
    43517,
    "STRONG",
    "toolkit/components/passwordmgr/test/browser/browser_preselect_login.js; browser_autofill_after_paint.js; "
    "browser_autocomplete_footer.js; browser_autocomplete_autofocus_with_frame.js; "
    "browser_autocomplete_disabled_readonly_passwordField.js; browser_focus_before_first_DOMContentLoaded.js; "
    "browser_username_select_dialog.js",
    "The login autocomplete dropdown toggling on a focused field at page load and filling the "
    "chosen credential, with one or several saved logins.",
    [2240907, 2240897, 2240898, 2240899],
)
C(
    43517,
    "STRONG",
    "toolkit/components/passwordmgr/test/browser/browser_context_menu.js; browser_context_menu_iframe.js; "
    "browser_context_menu_autocomplete_interaction.js",
    "The 'Fill Login' / 'Fill Password' context-menu entries, their position in the menu and "
    "keyboard-driven selection.",
    [2240903, 2240904, 2240905, 2251471, 2251472],
)
C(
    43517,
    "STRONG",
    "toolkit/components/passwordmgr/test/browser/browser_context_menu_generated_password.js; "
    "browser_doorhanger_generated_password.js; browser_autocomplete_generated_password_private_window.js",
    "'Suggest Strong Password' / 'Use a Securely Generated Password' from the context menu and "
    "from the autocomplete dropdown, on login and registration forms, on new-password fields, "
    "with and without an existing generated password, and its position in the menu.",
    [2240900, 2240901, 2240908, 2240909, 2240910, 2246559, 2246560, 2246561, 2246562,
     2251473, 2251509, 2251517],
)
C(
    43517,
    "STRONG",
    "toolkit/components/passwordmgr/test/browser/browser_autocomplete_insecure_warning.js; browser_autofill_http.js; "
    "browser_insecurePasswordConsoleWarning.js",
    "The insecure-connection warning in the dropdown, and which credentials are offered on the "
    "http vs https version of a site.",
    [2240911, 2240915, 2240916, 2246548, 2246549],
)
C(
    43517,
    "STRONG",
    "toolkit/components/passwordmgr/test/browser/browser_doorhanger_generated_password.js; "
    "browser_doorhanger_reveal_password.js",
    "Generated-password string specification, auto-save of a generated password, auto-save on "
    "edit, no second auto-save, reveal in the doorhanger, and the retype-field dropdown.",
    [2246557, 2246558, 2248176, 2248177, 2248178, 2248179, 2248180, 2248181, 2248182, 2248183],
)
# --- about:logins entry points and CRUD
C(
    43517,
    "STRONG",
    "toolkit/components/passwordmgr/test/browser/browser_openPasswordManager.js; browser_entry_point_telemetry.js; "
    "browser/components/aboutlogins/tests/browser/browser_openPreferences.js; browser_openPreferencesExternal.js; "
    "browser_openFiltered.js",
    "Reaching about:logins by direct navigation, from about:preferences, the hamburger menu, the "
    "password-field autocomplete footer and the context menu.",
    [2241080, 2241081, 2241082, 2241086, 2241087],
)
CSEC(
    43517,
    "STRONG",
    "browser/components/aboutlogins/tests/browser/browser_createLogin.js; browser_loginItemErrors.js; "
    "browser_tabKeyNav.js",
    "The Add Password form: required-field validation, saving a new login (including non-ASCII "
    "values), Cancel, and doing all of it by keyboard.",
    [410311, 410312],
    exclude=[2241110],  # "matches the design" - visual only
)
CSEC(
    43517,
    "STRONG",
    "browser/components/aboutlogins/tests/browser/browser_copyToClipboardButton.js; browser_openSite.js; "
    "browser_deleteLogin.js; browser_confirmDeleteDialog.js; browser_updateLogin.js; browser_tabKeyNav.js; "
    "browser_osAuthDialog.js",
    "The login item view: origin hyperlink, Copy username, Copy password, Show/Hide, Remove and "
    "its confirmation dialog, Edit-mode save - by mouse and by keyboard.",
    [410313, 410314, 410315, 410316, 410317],
)
CSEC(
    43517,
    "STRONG",
    "browser/components/aboutlogins/tests/browser/browser_loginFilter.js; browser_openFiltered.js; "
    "browser_noLoginsView.js",
    "The about:logins search bar: typing, no-results state, filtering by username / website / "
    "password, clearing, and keyboard operation.",
    [410318],
)
C(
    43517,
    "STRONG",
    "browser/components/aboutlogins/tests/browser/browser_loginSortOrderRestored.js; browser_loginListChanges.js; "
    "browser_tabKeyNav.js",
    "Sorting the login list by Name A-Z / Z-A, Last Used and Last Modified, the order persisting, "
    "and operating the Sort-by dropdown from the keyboard.",
    [2241478, 2241479, 2241476, 2241477, 2241458, 2241459, 2241460, 2241461, 2241462],
)
CSEC(
    43517,
    "STRONG",
    "browser/components/aboutlogins/tests/browser/browser_breachAlertShowingForAddedLogin.js; "
    "browser_breachAlertLinkTelemetry.js; browser_alertDismissedAfterChangingPassword.js; "
    "browser_vulnerableLoginAddedInSecondaryWindow.js; "
    "toolkit/components/satchel/megalist/content/tests/browser/browser_passwords_list_alerts.js",
    "Breached-account warning icon and banner, vulnerable-password icon and banner, and "
    "'Sort by Alerts' ordering.",
    [410501, 410502],
)
C(
    43517,
    "STRONG",
    "browser/components/aboutlogins/tests/browser/browser_fxAccounts.js",
    "Signing in to Sync from about:logins, the avatar state, and signing out.",
    [2241532, 2241533, 2241534],
)
C(
    43517,
    "STRONG",
    "browser/components/aboutlogins/tests/browser/browser_openImport.js",
    "The 'Import from Another Browser' entry in the Settings menu, including keyboard access.",
    [2241464, 2241465],
)
CSEC(
    43517,
    "STRONG",
    "browser/components/aboutlogins/tests/browser/browser_openImportCSV.js; "
    "toolkit/components/satchel/megalist/content/tests/browser/browser_passwords_sidebar_import_from_csv.js",
    "The whole CSV import flow: imported / updated / duplicate / empty / error-only files, the "
    "summary report, the missing-column error modal and a large file.",
    [677364, 677365, 677366, 677367, 677368, 677369, 677370, 677371, 677372, 677373],
)
C(
    43517,
    "STRONG",
    "browser/components/aboutlogins/tests/browser/browser_openExport.js; browser_primaryPassword.js; "
    "browser_osAuthDialog.js; "
    "toolkit/components/satchel/megalist/content/tests/browser/browser_passwords_export_success_notification.js",
    "The Export Passwords dialog, its dismissal, the OS file picker hand-off, writing the CSV, and "
    "the Primary-Password / OS-reauth gates on export.",
    [2241518, 2241519, 2241520, 2241521, 2241522, 2241527, 2241528],
)
# --- doorhangers
C(
    43517,
    "STRONG",
    "toolkit/components/passwordmgr/test/browser/browser_doorhanger_save_password.js; browser_doorhanger_remembering.js; "
    "browser_doorhanger_promptToChangePassword.js; browser_doorhanger_password_edits.js; "
    "browser_doorhanger_username_edits.js; browser_doorhanger_empty_password.js; "
    "browser_doorhanger_form_password_edit.js; browser_doorhanger_reveal_password.js; "
    "browser_doorhanger_autofill_then_save_password.js; browser_doorhanger_autocomplete_values.js; "
    "browser_doorhanger_replace_dismissed_with_visible_while_opening.js; browser_doorhanger_keyboard.js; "
    "browser_exceptions_dialog.js; browser_private_window.js",
    "The save / update / never-save doorhanger: saving credentials, updating a password, skipping "
    "the username, the dismissed (key-icon) state, adding or editing a username in the doorhanger, "
    "Show Password, re-showing after fields are cleared and refilled, the private-mode dismissed "
    "variant, adding an exception, and keyboard operation.",
    [2243012, 2243013, 2243014, 2243015, 2243016, 2243017, 2243018, 2243019, 2243020, 2243021,
     2244611, 2244612, 2244613, 2244614, 2244615, 2244616, 2244621, 2244620],
)
C(
    43517,
    "STRONG",
    "toolkit/components/passwordmgr/test/browser/browser_exceptions_dialog.js",
    "Adding and removing sites in the 'Ask to save passwords' exceptions list from "
    "about:preferences#privacy.",
    [2251510, 2251511],
)
# --- primary password / OS auth
C(
    43517,
    "STRONG",
    "browser/components/aboutlogins/tests/browser/browser_primaryPassword.js; "
    "toolkit/components/passwordmgr/test/browser/browser_autocomplete_primary_password.js; "
    "toolkit/components/satchel/megalist/content/tests/browser/browser_passwords_primary_password.js",
    "Setting, changing, removing and resetting a Primary Password, the prompt appearing when it is "
    "needed (viewing, copying, editing, revealing, about:logins access, autofill on a saved site), "
    "the dismissed-prompt warning bar, and generation being unavailable until it is unlocked.",
    [2245178, 2245179, 2245180, 2245181, 2245182, 2245183, 2245184,
     2245198, 2245199, 2245200, 2245201, 2245202, 2245203, 2245204, 2245205, 2245206,
     2245207, 2245208,
     2245191, 2245192, 2245193, 2245194, 2245195, 2245196, 2245197,
     2264687, 2264688, 2264689, 2264690,
     2244617, 2244618],
)
CSEC(
    43517,
    "STRONG",
    "browser/components/aboutlogins/tests/browser/browser_osAuthDialog.js; browser_primaryPassword.js",
    "The reauthentication dialog gating Show password / Copy password / Edit, its error state on "
    "an invalid password, setting a Primary Password through it, and it not appearing when not "
    "required.",
    [410715, 410716, 410717, 410718, 410719],
)
C(
    43517,
    "STRONG",
    "browser/components/aboutlogins/tests/browser/browser_osAuthDialog.js; browser_primaryPassword.js; "
    "browser/components/preferences/tests/browser_privacy_trustPanelBreachAlerts.js",
    "The OS-Authentication checkbox for passwords: default-off, enabling it prompts and requires a "
    "valid OS password, then reveal / copy / edit / create-Primary-Password in about:logins each "
    "prompt, the 5-minute grace window, the interaction with an existing Primary Password, "
    "no prompt when disabled, and the toggle telemetry.",
    [3078053, 3078032, 3078034, 3078035, 3078036, 3078039, 3078038, 3078037, 3078040,
     3078041, 3078042, 3078043, 3078047, 3078048, 3078044, 3078045, 3078046, 3078055,
     3078051, 3078052],
)
C(
    43517,
    "STRONG",
    "browser/extensions/formautofill/test/browser/creditCard/browser_creditCard_osAuth.js; "
    "browser/extensions/formautofill/test/browser/creditCard/browser_editCreditCardDialog.js",
    "The OS-Authentication checkbox for payment methods: default-off, enable/disable with a valid "
    "OS password, the prompt on credit-card autofill and on Edit Card, the locked-pref case, the "
    "private-mode case, no prompt when disabled, and the toggle telemetry.",
    [3078063, 3078064, 3078076, 3078066, 3078067, 3078077, 3078078, 3078071, 3078072,
     3078068, 3078073],
)
C(
    43517,
    "MEDIUM",
    "toolkit/components/passwordmgr/test/browser/browser_autocomplete_footer.js; "
    "toolkit/components/passwordmgr/test/unit/test_findRelatedRealms.js; browser_doorhanger_httpsUpgrade.js; "
    "browser_doorhanger_crossframe.js; browser_relay_use.js; browser_doorhanger_submit_telemetry.js; "
    "browser/components/aboutlogins/tests/browser/browser_openImport.js",
    "eTLD+1 / subdomain dropdown dedup is verified at xpcshell level, not as a dropdown UI flow. "
    "Per-browser import (Edge / IE / Chrome / Safari), the Settings menu contents, container-tab "
    "behaviour, generation telemetry and the no-username Fill-Login submenu are only partially "
    "covered.",
    [2240890, 2240891, 2240892, 2240893, 2240894, 2240895, 2240896,
     2240902, 2240906, 2240912, 2240913, 2240914,
     2241084, 2241085, 2241088, 2241110, 2241463, 2241492, 2241493, 2241494, 2241495,
     2241466, 2241467, 2241468, 2266228, 2241473, 2866176,
     2245185, 2245186, 2245187, 2245188, 2245189, 2245190,
     2246550, 2246551, 2246552, 2246553, 2246554, 2246555, 2246556,
     2248174, 2248175, 2248229, 2248230,
     2251465, 2251466, 2251467, 2251468, 2251469, 2251470,
     2251489, 2251490, 2251491, 2251492, 2251506, 2251507, 2251508,
     2251512, 2251513, 2251514, 2251515, 2251516,
     3078033, 3078058, 3078079, 3078080],
)
