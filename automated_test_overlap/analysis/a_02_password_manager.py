"""Round 5 -- tests/password_manager (46 linked STARfox tests).

The most duplicated STARfox suite in the whole comparison. Two tree directories cover it
almost exhaustively:

* browser/components/aboutlogins/tests/browser/ -- 29 tests, essentially one per about:logins
  interaction (create, update, delete, filter, copy, reveal, primary password, export,
  navigation in and out).
* toolkit/components/passwordmgr/test/browser/ -- 33 doorhanger / autocomplete / context-menu
  tests, including a dedicated one for nearly every doorhanger variant STARfox re-tests.

The exceptions are the live-site tests (google.com, reddit.com, facebook.com), which is real
coverage the tree deliberately does not attempt, and CSV export correctness.
"""

from ledger import T

AL = "browser/components/aboutlogins/tests/browser/"
PM = "toolkit/components/passwordmgr/test/browser/"
PW = "tests/password_manager/"

# ================================================================ about:logins CRUD
T(
    "STRONG",
    AL + "browser_createLogin.js; browser_loginListChanges.js",
    "browser_createLogin.js drives the Add Login form and asserts the stored login, including "
    "field validation -- the same flow as saving valid data and saving non-ASCII characters.",
    [
        PW + "test_add_password_save_valid_data.py",
        PW + "test_add_password_non_ascii_chars.py",
    ],
)
T(
    "STRONG",
    AL + "browser_updateLogin.js; browser_loginItemErrors.js",
    "browser_updateLogin.js edits a login in place and asserts the change is persisted.",
    [PW + "test_changes_made_in_edit_mode_are_saved.py"],
)
T(
    "STRONG",
    AL
    + "browser_deleteLogin.js; browser_confirmDeleteDialog.js; browser_removeAllDialog.js",
    "Deleting a login, including the confirmation dialog, has three dedicated tests.",
    [PW + "test_delete_login.py"],
)
T(
    "STRONG",
    AL + "browser_loginFilter.js; browser_openFiltered.js",
    "browser_loginFilter.js filters the login list by site, username and password text and "
    "asserts which entries survive -- the three searches these tests split apart.",
    [
        PW + "test_about_logins_search_website.py",
        PW + "test_about_logins_search_username.py",
        PW + "test_about_logins_search_passwords.py",
    ],
)
T(
    "STRONG",
    AL + "browser_copyToClipboardButton.js",
    "A test dedicated to the username and password copy buttons and what lands on the "
    "clipboard.",
    [
        PW + "test_about_logins_username_copy_button.py",
        PW + "test_about_logins_password_copy_button.py",
    ],
)
T(
    "STRONG",
    AL + "browser_loginItemErrors.js; browser_primaryPassword.js; browser_tabKeyNav.js",
    "The reveal/hide password toggle is asserted as part of the login-item tests and again "
    "under primary password.",
    [PW + "test_about_logins_password_show_hide_button.py"],
)
T(
    "STRONG",
    AL + "browser_openSite.js",
    "browser_openSite.js clicks the origin hyperlink on a saved login and asserts the tab that "
    "opens.",
    [PW + "test_saved_hyperlink_redirects_to_corresponding_page.py"],
)

# ================================================================ about:logins entry points
T(
    "STRONG",
    AL + "browser_openPreferences.js; browser_openPreferencesExternal.js; "
    "browser/components/preferences/tests/privacy/browser_privacy_passwordGenerationAndAutofill.js",
    "Navigating between about:preferences and about:logins is covered from both directions.",
    [PW + "test_about_logins_navigation_from_about_preferences.py"],
)
T(
    "PARTIAL",
    AL + "browser_openPreferences.js; "
    "browser/components/customizableui/test/browser_947914_button_history.js",
    "about:logins itself is well covered, but nothing in the tree opens it from the hamburger "
    "menu's Passwords entry -- the app-menu route is asserted for other panel items, not this "
    "one.",
    [PW + "test_about_logins_navigation_from_hamburger_menu.py"],
)
T(
    "STRONG",
    AL + "browser_contextmenuFillLogins.js; " + PM + "browser_context_menu.js; "
    "browser_context_menu_autocomplete_interaction.js",
    "The field context menu's 'Use Saved Password' entry, and the about:logins navigation it "
    "offers, are covered by the context-menu tests on both sides.",
    [
        PW + "test_about_logins_navigation_from_context_menu.py",
        PW + "test_navigation_to_about_logins_from_autocomplete.py",
    ],
)
T(
    "STRONG",
    PM + "browser_context_menu.js; browser_context_menu_iframe.js",
    "browser_context_menu.js asserts the 'Use Saved Password' item is absent when there are no "
    "saved logins, for both the username and the password field.",
    [
        PW
        + "test_use_saved_password_option_not_in_password_field_context_menu_without_saved_logins.py",
        PW
        + "test_use_saved_password_option_not_in_username_field_context_menu_without_saved_logins.py",
    ],
)

# ================================================================ doorhanger
T(
    "STRONG",
    PM + "browser_doorhanger_save_password.js; browser_doorhanger_remembering.js; "
    "browser_doorhanger_submit_telemetry.js",
    "Saving a login from the doorhanger is the subject of three tests.",
    [PW + "test_save_login_via_doorhanger.py"],
)
T(
    "STRONG",
    PM + "browser_doorhanger_remembering.js; browser_doorhanger_save_password.js",
    "The 'Never save' path and the resulting exception are covered by "
    "browser_doorhanger_remembering.js.",
    [PW + "test_never_save_login_via_doorhanger.py"],
)
T(
    "STRONG",
    PM
    + "browser_doorhanger_password_edits.js; browser_doorhanger_promptToChangePassword.js; "
    "browser_doorhanger_form_password_edit.js",
    "Updating an existing login from the doorhanger, including the change-password prompt.",
    [PW + "test_update_login_via_doorhanger.py"],
)
T(
    "STRONG",
    PM
    + "browser_doorhanger_username_edits.js; browser_doorhanger_autocomplete_values.js",
    "browser_doorhanger_username_edits.js adds and edits the username in the doorhanger and "
    "asserts what is captured, including from the dismissed state.",
    [
        PW + "test_add_username_via_doorhanger.py",
        PW + "test_username_edit_captured_in_dismissed_doorhanger.py",
    ],
)
T(
    "STRONG",
    PM + "browser_doorhanger_empty_password.js; "
    "browser_doorhanger_replace_dismissed_with_visible_while_opening.js; "
    "browser_doorhanger_urlbar_focus.js",
    "A password-only form producing a dismissed rather than visible doorhanger, and the key "
    "icon that remains in the urlbar afterwards, are both covered.",
    [
        PW + "test_password_field_only_triggers_dismissed_doorhanger.py",
        PW + "test_password_manager_key_icon_after_doorhanger_dismiss.py",
    ],
)
T(
    "STRONG",
    PM + "browser_autocomplete_generated_password_private_window.js; "
    "browser_doorhanger_generated_password.js",
    "The private-window doorhanger behaviour for credentials is covered by the private-window "
    "generated-password test.",
    [PW + "test_private_browsing_dismiss_doorhanger_credentials.py"],
)
T(
    "STRONG",
    PM + "browser_doorhanger_reveal_password.js; browser_doorhanger_keyboard.js",
    "browser_insecurePasswordConsoleWarning.js and browser_autocomplete_insecure_warning.js "
    "cover the insecure-login warning in the console and in the autocomplete dropdown.",
    [PW + "test_insecure_password.py"],
)

# ================================================================ generated passwords
T(
    "STRONG",
    PM
    + "browser_doorhanger_generated_password.js; browser_context_menu_generated_password.js; "
    "browser_autocomplete_generated_password_private_window.js",
    "browser_doorhanger_generated_password.js covers the generated password being auto-saved and "
    "then edited, which re-triggers the save; browser_context_menu_generated_password.js covers "
    "the context-menu entry point and the options it offers.",
    [
        PW + "test_auto_saved_generated_password_context_menu.py",
        PW + "test_edit_generated_password_triggers_autosave.py",
        PW
        + "test_confirm_or_edit_generated_password_shows_previously_edited_and_generated_password_options.py",
    ],
)

# ================================================================ autocomplete dropdown
T(
    "STRONG",
    PM
    + "browser_autocomplete_autofocus_with_frame.js; browser_autocomplete_footer.js; "
    "browser_autocomplete_disabled_readonly_passwordField.js",
    "Whether the autocomplete dropdown opens for a focused login field on page load is covered "
    "by the autofocus test.",
    [
        PW
        + "test_autocomplete_dropdown_is_toggled_for_focused_login_fields_on_page_load.py"
    ],
)
T(
    "STRONG",
    AL
    + "browser_loginListChanges.js; browser_loginSortOrderRestored.js; "
    + PM
    + "browser_autocomplete_footer.js",
    "Several saved logins for one origin, and the order they are offered in, are covered by the "
    "login-list and autocomplete-footer tests.",
    [PW + "test_multiple_saved_logins.py"],
)

# ================================================================ primary password
T(
    "STRONG",
    AL
    + "browser_primaryPassword.js; browser_osAuthDialog.js; "
    + PM
    + "browser_autocomplete_primary_password.js",
    "browser_primaryPassword.js is dedicated to the primary-password gate on about:logins: it "
    "asserts the prompt appears on access, on copy and on edit, and what is visible once it is "
    "satisfied or dismissed.",
    [
        PW + "test_about_logins_copy_prompts_primary_password.py",
        PW + "test_about_logins_edit_prompts_primary_password.py",
        PW + "test_can_view_password_when_PP_enabled.py",
        PW + "test_primary_password_triggered_on_about_logins_access.py",
        PW + "test_edit_autofill_after_pp_dismissed.py",
    ],
)
T(
    "STRONG",
    PM + "browser_autocomplete_primary_password.js; "
    "browser_context_menu_generated_password.js",
    "With a primary password set and no stored credentials, the generated-password options are "
    "suppressed -- covered by the primary-password autocomplete test.",
    [PW + "test_no_generated_password_options_with_pp_and_no_credentials.py"],
)

# ================================================================ partial
T(
    "PARTIAL",
    "browser/components/preferences/tests/privacy/browser_privacy_passwordGenerationAndAutofill.js; "
    + AL
    + "browser_primaryPassword.js",
    "Setting, changing and removing the primary password from about:preferences is only "
    "partially covered: the tree asserts the pref and the resulting prompt, but not the "
    "three-way add / edit / delete lifecycle in the preferences dialog.",
    [
        PW + "test_add_primary_password.py",
        PW + "test_edit_primary_password.py",
        PW + "test_delete_primary_password.py",
    ],
)
T(
    "PARTIAL",
    AL + "browser_openExport.js; browser_openImportCSV.js",
    "browser_openExport.js covers the export flow being launched and the file picker, but not "
    "the contents of the written CSV, which is what test_password_csv_correctness.py checks. "
    "The primary-password-then-export combination is also not covered.",
    [
        PW + "test_password_csv_export.py",
        PW + "test_password_csv_correctness.py",
        PW + "test_primary_password_allows_csv_export.py",
    ],
)

# ================================================================ unique
T(
    "UNIQUE",
    "n/a",
    "Live-site password-manager checks against google.com, reddit.com and facebook.com. The "
    "tree does not test against the live web, so these three are STARfox's own coverage -- and "
    "the only automated defence against a real site's login form changing shape.",
    [
        PW + "test_password_manager_on_google_US.py",
        PW + "test_password_manager_on_reddit.py",
        PW + "test_facebook_login_autofill_dropdown.py",
    ],
)
