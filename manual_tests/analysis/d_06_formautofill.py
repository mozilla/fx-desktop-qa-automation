from _ledger import C, CSEC

# ---------------------------------------------------------------- suite 2054
# "Form Autofill" (222 cases). Tree: browser/extensions/formautofill/test/browser/ = 157
# browser-chrome tests (address/, creditCard/ and the shared root). This is one of the
# best-automated areas in the whole tree.
C(
    2054,
    "STRONG",
    "browser/extensions/formautofill/test/browser/browser_privacyPreferences.js; "
    "browser/extensions/formautofill/test/browser/browser_manageAddressesDialog.js; "
    "browser/extensions/formautofill/test/browser/address/browser_manageAddressesSubpage.js; "
    "browser/extensions/formautofill/test/browser/browser_editAddressDialog.js",
    "The about:preferences form-autofill switches, and creating / editing / removing a saved "
    "address from the Saved Addresses dialog.",
    [122347, 102379, 122348, 122349, 122350, 2867646, 122353],
)
C(
    2054,
    "STRONG",
    "browser/extensions/formautofill/test/browser/address/browser_address_doorhanger_display.js; "
    "browser_address_doorhanger_ui.js; browser_address_doorhanger_ui_lines.js; "
    "browser_address_doorhanger_confirmation_popup.js; browser_address_doorhanger_state.js; "
    "browser_address_doorhanger_tel.js; browser_address_doorhanger_postalcode.js; "
    "browser_address_doorhanger_required_fields.js; browser_address_doorhanger_invalid_fields.js; "
    "browser_address_doorhanger_not_shown.js; browser_address_doorhanger_non_mergeable_fields.js; "
    "browser_address_doorhanger_multiple_tabs.js; browser_address_doorhanger_unsupported_region.js; "
    "browser_edit_address_doorhanger_display.js; browser_edit_address_doorhanger_save_edited_fields.js; "
    "browser_edit_address_doorhanger_display_state.js; browser_address_capture_page_navigation.js; "
    "browser_address_capture_form_removal.js; browser_address_capture_before_fields_identified.js; "
    "browser_address_capture_trimmed_data.js; browser_address_capture_housenumber.js",
    "21 dedicated tests for the address capture/save/update doorhanger, including editing before "
    "saving and every not-shown condition.",
    [122352, 122354, 122351, 2886580, 2886581],
)
C(
    2054,
    "STRONG",
    "browser/extensions/formautofill/test/browser/browser_autofill_address_name.js; "
    "browser_autofill_address_level.js; browser_autofill_address_select.js; browser_autofill_address_textarea.js; "
    "browser_autofill_address_housenumber.js; browser_address_heuristics_autofill_name.js; "
    "browser_collectFormFields.js; browser_label_matching.js; browser_phonenumber.js; browser_phonenumber_country.js; "
    "browser/extensions/formautofill/test/browser/address/browser_address_street_lookup.js",
    "Field detection and autofill by @autocomplete attribute and by heuristics, for name, street, "
    "address level, email and telephone - plus the telephone-format matrix.",
    [122355, 122356, 122357, 122358, 122360, 122361, 122362, 122384, 122386, 130028],
)
C(
    2054,
    "STRONG",
    "browser/extensions/formautofill/test/browser/browser_previewFormFields.js; browser_clearPopulatedForm.js; "
    "browser_fillclear_events.js; browser_autocomplete_footer.js; browser_dropdown_layout.js; "
    "browser_email_dropdown.js",
    "The autocomplete dropdown, hover preview (incl. the yellow highlight), Clear Form and the "
    "footer entries ('Manage addresses').",
    [122359, 122368, 122574, 2742137],
)
C(
    2054,
    "STRONG",
    "browser/extensions/formautofill/test/browser/browser_autocomplete_marked_detached_tab.js; "
    "browser_autocomplete_marked_back_forward.js; browser_form_changes.js; browser_dynamic_form_autocompletion.js; "
    "browser_dynamic_form_detection.js; browser_dynamic_form_refill_on_site_clearing_values.js",
    "Dropdown behaviour when the tab is dragged to a new window, on back/forward, and on "
    "dynamically-changing forms.",
    [122367, 122385, 122387],
)
C(
    2054,
    "STRONG",
    "browser/extensions/formautofill/test/browser/browser_submission_in_private_mode.js; "
    "browser/components/privatebrowsing/test/browser/browser_privatebrowsing_permissions.js",
    "Autofill still fills in a private window but new/updated profiles are not persisted from one.",
    [122363, 101666, 101669, 605536, 122394, 101667, 101668, 122587],
)
C(
    2054,
    "STRONG",
    "browser/extensions/formautofill/test/browser/browser_autocomplete_region.js; "
    "browser/extensions/formautofill/test/browser/browser_autofill_address_select_inexact.js; "
    "browser_autofill_address_select_match_isoid.js",
    "Region-specific address forms (CA / DE) and matching of select-element values.",
    [605537, 605538],
)
# --- credit card
C(
    2054,
    "STRONG",
    "browser/extensions/formautofill/test/browser/creditCard/browser_creditCard_doorhanger_display.js; "
    "browser_creditCard_doorhanger_action.js; browser_creditCard_doorhanger_fields.js; "
    "browser_creditCard_doorhanger_not_shown.js; browser_creditCard_doorhanger_logo.js; "
    "browser_creditCard_capture_page_navigation.js; browser_creditCard_capture_form_removal.js; "
    "browser_creditCard_capture_multiple_cc_number.js; browser_creditCard_submission_normalized.js; "
    "browser_creditCard_submission_autodetect_type.js",
    "The credit-card capture doorhanger: displayed, Save, Not now, Update, field contents, "
    "card-type logo and every not-shown condition.",
    [122392, 122399, 2299610, 122406, 3056981, 3056982],
)
C(
    2054,
    "STRONG",
    "browser/extensions/formautofill/test/browser/creditCard/browser_editCreditCardDialog.js; "
    "browser/extensions/formautofill/test/browser/browser_privacyPreferences.js",
    "Create / edit / delete a saved card, and the 'Save and fill payment methods' switch.",
    [122389, 122390, 122391, 122388, 102380, 131344, 3056980],
)
C(
    2054,
    "STRONG",
    "browser/extensions/formautofill/test/browser/creditCard/browser_creditCard_dropdown_layout.js; "
    "browser_creditCard_heuristics.js; browser_autofill_creditCard_expiry.js; browser_autofill_creditCard_name.js; "
    "browser_autofill_creditCard_type.js; browser_creditCard_preview_cleared_on_pointer_leave.js; "
    "browser/extensions/formautofill/test/browser/browser_previewFormFields.js; browser_clearPopulatedForm.js",
    "Credit-card autofill: suggestions on every eligible field, preview on hover, filling the "
    "right data, the yellow highlight and Clear Form.",
    [122407, 122396, 122401, 122404, 122405, 2299612, 2299614, 122581,
     3056983, 3056984, 3056985, 3056986, 3056987],
)
C(
    2054,
    "STRONG",
    "browser/extensions/formautofill/test/browser/creditCard/browser_insecure_form.js; browser_anti_clickjacking.js; "
    "browser_creditCard_fill_cancel_login.js; browser_creditCard_osAuth.js",
    "Credit-card autofill suppressed on insecure/untrusted forms, the anti-clickjacking delay and "
    "the OS-auth gate.",
    [122398],
)
C(
    2054,
    "STRONG",
    "browser/extensions/formautofill/test/browser/creditCard/browser_creditCard_doorhanger_keyboard.js; "
    "browser/extensions/formautofill/test/browser/browser_previewFormFields.js",
    "Keyboard-only interaction with the autofill dropdown and doorhanger.",
    [122366, 122578, 122585],
)
C(
    2054,
    "STRONG",
    "browser/extensions/formautofill/test/browser/creditCard/browser_creditCard_doorhanger_sync.js",
    "The credit-card doorhanger's sync-enabled variant.",
    [122410],
)
C(
    2054,
    "STRONG",
    "browser/extensions/formautofill/test/browser/address/browser_address_telemetry.js; "
    "browser/extensions/formautofill/test/browser/browser_dynamic_form_telemetry.js; "
    "browser/extensions/formautofill/test/browser/creditCard/browser_creditCard_telemetry_autofill.js; "
    "browser_creditCard_telemetry_popup.js; browser_creditCard_telemetry_manage.js; "
    "browser_creditCard_telemetry_submit_new.js; browser_creditCard_telemetry_submit_update.js",
    "The detected / popup_shown / filled / filled_modified event methods for both address and "
    "credit-card forms.",
    [2551748, 2551749, 2551750, 2551751, 2551753, 2551754, 2551755, 2551756],
)
# --- the "unified autocomplete" per-field matrices
CSEC(
    2054,
    "STRONG",
    "browser/extensions/formautofill/test/browser/browser_autocomplete_footer.js; browser_previewFormFields.js; "
    "browser_clearPopulatedForm.js; browser_dropdown_layout.js; browser_email_dropdown.js; "
    "browser_manageAddressesDialog.js; browser_collectFormFields.js; browser_label_matching.js; "
    "browser_autofill_address_name.js; browser_autofill_address_level.js; browser_autofill_address_textarea.js; "
    "browser_phonenumber.js",
    "MATRIX: sections 542292/542293/542294 repeat three checks (dropdown is unified / preview+fill "
    "works / Clear Form / Manage addresses) once per address field. The tree covers the dropdown "
    "composition, preview, fill, clear and footer generically across all detected field types. "
    "Recommendation: keep one field per section as a smoke representative.",
    [542292, 542293, 542294],
)
CSEC(
    2054,
    "STRONG",
    "browser/extensions/formautofill/test/browser/creditCard/browser_creditCard_dropdown_layout.js; "
    "browser_creditCard_heuristics.js; browser_autofill_creditCard_expiry.js; browser_autofill_creditCard_name.js; "
    "browser/extensions/formautofill/test/browser/browser_previewFormFields.js; browser_clearPopulatedForm.js; "
    "browser_autocomplete_footer.js",
    "MATRIX: sections 542299/542300/542301 are the same three checks repeated per credit-card "
    "field (incl. 'not offered on the CSC field', which browser_creditCard_heuristics.js asserts).",
    [542299, 542300, 542301],
)
CSEC(
    2054,
    "STRONG",
    "browser/extensions/formautofill/test/browser/browser_previewFormFields.js; browser_clearPopulatedForm.js; "
    "browser_collectFormFields.js; browser_email_dropdown.js; browser_phonenumber.js; "
    "browser/extensions/formautofill/test/browser/address/browser_address_doorhanger_display.js; "
    "browser_address_doorhanger_required_fields.js; "
    "browser/extensions/formautofill/test/browser/browser_managePersonalInfoSubpage.js",
    "MATRIX: sections 580065/580066/580067 repeat dropdown/preview/fill/highlight/clear/capture "
    "once per field group (name-org, address, phone-email). Same generic mechanics in-tree.",
    [580065, 580066, 580067],
)
C(
    2054,
    "MEDIUM",
    "browser/extensions/formautofill/test/browser/creditCard/browser_creditCard_doorhanger_sync.js; "
    "browser/extensions/formautofill/test/browser/browser_autofill_invisible_fields.js; browser_nested_forms.js; "
    "browser_iframe_cross_origin_autofill.js",
    "Sync between two profiles, real-site/locale runs (amazon, FR/DE/CA top sites), and every "
    "HCM / RTL / theme / screen-reader / scroll-zoom variant have no in-tree analog. Form-history "
    "coexistence and the 'Saved Addresses grid' rendering cases are also not asserted upstream.",
    [122380, 122381, 122382, 122383, 122408, 122409, 122369,
     122364, 2692859, 122365, 2693737, 122395, 122397,
     605532, 605533, 605534, 605535,
     122575, 122589, 122591, 122603, 605541, 122597, 605539, 605540, 605542, 605543,
     2546918, 2547175, 2547177, 2742133, 2742134, 2742135, 2742136,
     2547211, 2547212, 2547213, 2547214, 2554822, 2547218, 2547219, 2547220],
)

# ---------------------------------------------------------------- suite 100943
# "Saved credentials autofill dropdown" (38 cases)
C(
    100943,
    "STRONG",
    "toolkit/components/passwordmgr/test/browser/browser_preselect_login.js; browser_autofill_after_paint.js; "
    "browser_autocomplete_footer.js; browser_autofill_track_filled_logins.js; "
    "browser_autocomplete_disabled_readonly_passwordField.js; browser_autofill_hidden_document.js; "
    "browser_focus_before_first_DOMContentLoaded.js",
    "The login autocomplete dropdown appearing on focus after page load, and filling the selected "
    "credential into the form.",
    [4078310, 4124770, 4078311, 4124768],
)
C(
    100943,
    "STRONG",
    "browser/extensions/formautofill/test/browser/browser_previewFormFields.js; browser_clearPopulatedForm.js; "
    "browser_autofill_address_name.js; "
    "browser/extensions/formautofill/test/browser/creditCard/browser_creditCard_dropdown_layout.js",
    "Selecting a saved address / credit card from the same unified dropdown, plus preview, "
    "highlight and Clear Form.",
    [4078378, 4078482, 4124453],
)
C(
    100943,
    "STRONG",
    "toolkit/components/satchel/test/browser/browser_autocomplete.js; browser_popup_mouseover.js; "
    "browser_close_tab.js; toolkit/components/passwordmgr/test/browser/browser_form_history_fallback.js",
    "Plain form-history suggestions: filling one, none shown when the store is empty, and never "
    "offered on password fields.",
    [4120743, 4120977, 4121137],
)
C(
    100943,
    "STRONG",
    "toolkit/components/passwordmgr/test/browser/browser_autocomplete_import.js",
    "The 'import your passwords' suggestion row: shown only with no saved logins, suppressed by "
    "signon.suggestImportCount, and suppressed when the other browser has no matching login.",
    [4120976, 4121248, 4121249],
)
C(
    100943,
    "STRONG",
    "toolkit/components/passwordmgr/test/browser/browser_context_menu_generated_password.js; "
    "browser_doorhanger_generated_password.js; browser_autocomplete_generated_password_private_window.js",
    "'Use a Securely Generated Password': generated, filled and auto-saved; only offered on "
    "password fields.",
    [4121252, 4124425],
)
C(
    100943,
    "STRONG",
    "toolkit/components/passwordmgr/test/browser/browser_autocomplete_insecure_warning.js; browser_autofill_http.js",
    "The insecure-form warning in the dropdown on HTTP vs HTTPS login forms.",
    [4124458],
)
C(
    100943,
    "STRONG",
    "toolkit/components/passwordmgr/test/browser/browser_autocomplete_primary_password.js; "
    "browser/components/aboutlogins/tests/browser/browser_osAuthDialog.js; "
    "browser/extensions/formautofill/test/browser/creditCard/browser_creditCard_osAuth.js",
    "Autofill gated behind a Primary Password and behind OS authentication, including the "
    "Suggest-Strong-Password variant.",
    [4124771, 4124772, 4124773],
)
C(
    100943,
    "STRONG",
    "toolkit/components/passwordmgr/test/browser/browser_private_window.js; "
    "browser/extensions/formautofill/test/browser/browser_submission_in_private_mode.js",
    "In a private window autofill still works, new logins are saved but new addresses / cards are not.",
    [4078312, 4078388, 4078485],
)
C(
    100943,
    "STRONG",
    "toolkit/components/passwordmgr/test/browser/browser_context_menu_autocomplete_interaction.js; "
    "browser/components/aboutlogins/tests/browser/browser_tabKeyNav.js",
    "Keyboard navigation through the dropdown.",
    [4121253],
)
C(
    100943,
    "MEDIUM",
    "toolkit/components/passwordmgr/test/browser/browser_openPasswordManager.js; browser_entry_point_telemetry.js; "
    "browser_autocomplete_footer.js",
    "The Edit button entry point, passkey suggestions, dropdown ordering across sources, "
    "form-history deletion, and every visual/RTL/HCM/screen-reader/truncation/scroll case are "
    "not covered at this altitude in-tree.",
    [4124763, 4124775, 4124777, 4122407, 4122408, 4122409, 4122410, 4078314,
     4122411, 4124427, 4124434, 4124446, 4121247, 4124729, 4146331],
)