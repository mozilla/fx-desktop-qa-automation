"""Round 5 -- tests/pdf_viewer (20), tests/downloads (19), tests/sidebar (24),
tests/form_autofill (19).

Form autofill is the most one-sided comparison in this round after password manager:
browser/extensions/formautofill/test/browser/ has 55 tests and covers essentially every
address and credit-card flow STARfox re-tests, including the management dialogs.

The sidebar is the opposite. browser/components/sidebar/tests/browser/ has 51 tests, but they
are weighted towards the *panels* (bookmarks, history, synced tabs, extensions) while the
STARfox suite is almost entirely about **vertical tabs** -- a surface the tree tests only
glancingly. That makes the sidebar the strongest UNIQUE cluster in this round.

pdf_viewer splits cleanly: the viewer-integration rows duplicate
toolkit/components/pdfjs/test/, while the AcroForm interaction rows (typing into fields,
copy/paste, dropdowns, checkboxes, zoom inside fields) are upstream mozilla/pdf.js territory
and have no in-tree counterpart.
"""

from ledger import T

FA = "browser/extensions/formautofill/test/browser/"
FACC = "browser/extensions/formautofill/test/browser/creditCard/"
FAA = "browser/extensions/formautofill/test/browser/address/"
DL = "browser/components/downloads/test/browser/"
DLP = "browser/components/preferences/tests/downloads/"
APP = "browser/components/preferences/tests/applications/"
PDFJS = "toolkit/components/pdfjs/test/"
SB = "browser/components/sidebar/tests/browser/"
GENAI = "browser/components/genai/tests/browser/"

P = "tests/pdf_viewer/"
D = "tests/downloads/"
S = "tests/sidebar/"
F = "tests/form_autofill/"

# ================================================================ form autofill: addresses
T(
    "STRONG",
    FA + "browser_editAddressDialog.js; browser_manageAddressesDialog.js; "
    "browser_managePersonalInfoSubpage.js",
    "browser_editAddressDialog.js creates and edits a saved address through the same dialog, and "
    "browser_manageAddressesDialog.js covers the management list -- together the create / update "
    "pair these STARfox tests split.",
    [
        F + "test_create_profile_autofill.py",
        F + "test_updating_address.py",
    ],
)
T(
    "STRONG",
    FA + "browser_autofill_address_name.js; browser_autofill_address_level.js; "
    "browser_autofill_address_housenumber.js; browser_autofill_address_select.js; "
    "browser_autofill_address_textarea.js; browser_label_matching.js; "
    "browser_collectFormFields.js",
    "Field-level autofill is covered per attribute: the name tests for name fields, the address "
    "level / house-number tests for address parts, and browser_label_matching.js plus "
    "browser_collectFormFields.js for how fields are recognised in the first place -- which is "
    "what the three 'autofill_attribute' tests check.",
    [
        F + "test_address_autofill_attribute.py",
        F + "test_name_autofill_attribute.py",
        F + "test_telephone_autofill_attribute.py",
    ],
)
T(
    "STRONG",
    FA + "browser_clearPopulatedForm.js; browser_fillclear_events.js",
    "browser_clearPopulatedForm.js fills a form from a saved profile and then clears it, "
    "asserting the fields empty again -- for both the address and the credit-card case.",
    [
        F + "test_clear_form.py",
        F + "test_cc_clear_form.py",
    ],
)
T(
    "STRONG",
    FA + "browser_autocomplete_footer.js; browser_email_dropdown.js; "
    "browser_dropdown_layout.js; browser_dynamic_form_autocompletion.js",
    "The autofill suggestion dropdown, its layout and its footer are covered by four tests.",
    [F + "test_form_autofill_suggestions.py"],
)

# ================================================================ form autofill: credit cards
T(
    "STRONG",
    FA + "browser_autofill_creditCard_name.js; browser_autofill_creditCard_expiry.js; "
    "browser_autofill_creditCard_type.js; browser_iframe_autofill_cc_number.js; "
    "browser_fathom_cc.js",
    "Credit-card autofill is covered field by field -- name, expiry, type, number, including the "
    "iframe case and the Fathom-based field detection -- which subsumes the four-field and CVV "
    "variants.",
    [
        F + "test_autofill_credit_card.py",
        F + "test_autofill_credit_card_four_fields.py",
        F + "test_autofill_cc_cvv.py",
    ],
)
T(
    "STRONG",
    FACC
    + "browser_creditCard_doorhanger_display.js; browser_creditCard_doorhanger_action.js; "
    "browser_creditCard_doorhanger_fields.js; browser_creditCard_doorhanger_not_shown.js; "
    + FA
    + "browser_iframe_capture.js",
    "Five dedicated tests cover the save-credit-card doorhanger: when it is displayed, when it is "
    "suppressed, its fields, and each action it offers.",
    [F + "test_autofill_credit_card_doorhanger.py"],
)
T(
    "STRONG",
    FACC
    + "browser_creditCard_doorhanger_action.js; browser_creditCard_capture_form_removal.js; "
    + FA
    + "browser_managePersonalInfoSubpage.js; "
    + FAA
    + "browser_manageAddressesSubpage.js",
    "The doorhanger action test covers saving and updating a card, and the manage subpages cover "
    "the saved-card list where a card is edited or removed.",
    [
        F + "test_create_new_cc_profile.py",
        F + "test_edit_credit_card.py",
        F + "test_delete_cc_profile.py",
        F + "test_updating_credit_card.py",
    ],
)
T(
    "STRONG",
    "browser/components/preferences/tests/privacy/browser_privacy_passwordGenerationAndAutofill.js; "
    + FA
    + "browser_check_installed.js; "
    + FACC
    + "browser_creditCard_heuristics.js",
    "The preference that enables or disables autofill, for addresses and for cards, and the "
    "resulting behaviour.",
    [
        F + "test_enable_disable_autofill.py",
        F + "test_autofill_credit_card_enable.py",
    ],
)
T(
    "STRONG",
    FA + "browser_submission_in_private_mode.js; browser_iframe_capture.js",
    "Nothing being captured from a private window is asserted by the private-browsing autofill "
    "test.",
    [F + "test_private_mode_info_not_saved.py"],
)

# ================================================================ downloads
T(
    "STRONG",
    DLP
    + "browser_downloads_handle_new_file_types.js; browser_downloads.js; "
    + APP
    + "browser_filetype_dialog.js; browser_change_app_handler.js; "
    "browser_applications_selection.js",
    "browser_downloads_handle_new_file_types.js adds a handler for a newly-seen MIME type, and "
    "the applications tests cover changing an existing handler and the Always Ask choice -- which "
    "is the whole of these three STARfox tests.",
    [
        D + "test_add_mime_type_doc.py",
        D + "test_add_zip_type.py",
        D + "test_set_always_ask_file_type.py",
    ],
)
T(
    "STRONG",
    DLP + "browser_downloads.js; browser_bug1547020_lockedDownloadDir.js; "
    "browser_open_download_preferences.js",
    "Changing the download directory from preferences, including the locked-directory case.",
    [D + "test_change_download_folder.py"],
)
T(
    "STRONG",
    DL + "browser_downloads_panel_block.js; browser_blocked_and_deleted_status.js; "
    "browser_confirm_unblock_download.js; browser_download_spam_protection.js",
    "The malicious-download warning, its panel state and the unblock confirmation.",
    [D + "test_download_malicious_warning.py"],
)
T(
    "STRONG",
    DL
    + "browser_downloads_context_menu_delete_file.js; browser_downloads_pauseResume.js; "
    "browser_download_failed_msg.js",
    "Deleting a download while it is still running.",
    [D + "test_delete_download_while_in_progress.py"],
)
T(
    "STRONG",
    DL
    + "browser_pdfjs_preview.js; browser_basic_functionality.js; "
    + PDFJS
    + "browser_pdfjs_download_button.js",
    "Downloading a PDF and what the panel shows for it.",
    [D + "test_download_pdf.py"],
)
T(
    "STRONG",
    "browser/base/content/test/contextMenu/browser_save_image.js; "
    + DL
    + "browser_basic_functionality.js; browser_download_is_clickable.js",
    "Starting a download from the page context menu.",
    [D + "test_download_pdf_from_context_menu.py"],
)
T(
    "STRONG",
    DL + "browser_image_mimetype_issues.js; browser_tempfilename.js; "
    "browser_download_starts_in_tmp.js; browser_downloads_jsonview.js",
    "The extension shown for a downloaded file, including where the MIME type and the URL "
    "disagree, is covered by browser_image_mimetype_issues.js and the temp-filename tests.",
    [
        D + "test_download_exe_and_check_extesion.py",
        D + "test_download_mp3_and_check_extension.py",
        D + "test_download_epub_shows_extension_in_downloads_panel.py",
    ],
)
T(
    "STRONG",
    "dom/security/test/https-first/browser_mixed_content_download.js; "
    "dom/security/test/mixedcontentblocker/browser_test_mixed_content_download.js; "
    + DL
    + "browser_downloads_panel_block.js",
    "A mixed-content download over an HTTPS page being blocked.",
    [D + "test_mixed_content_download_via_https.py"],
)

# ================================================================ pdf viewer
T(
    "STRONG",
    PDFJS
    + "browser_pdfjs_navigation.js; browser_pdfjs_views.js; browser_pdfjs_main.js",
    "browser_pdfjs_navigation.js walks the viewer's page navigation controls.",
    [P + "test_pdf_navigation.py"],
)
T(
    "STRONG",
    PDFJS + "browser_pdfjs_zoom.js",
    "test and test_browser_zoom step through the viewer's zoom levels.",
    [P + "test_zoom_pdf_viewer.py"],
)
T(
    "STRONG",
    PDFJS + "browser_pdfjs_download_button.js; browser_pdfjs_savedialog.js; "
    "browser_pdfjs_saveas.js",
    "Downloading the open PDF through the viewer's own download button and the resulting save "
    "dialog.",
    [P + "test_pdf_download.py"],
)
T(
    "STRONG",
    PDFJS + "browser_pdfjs_saveas.js",
    "test_pdf_saveas_forms writes the filled document and re-reads its field values, which is "
    "what both of these check.",
    [
        P + "test_download_pdf_with_form_fields.py",
        P + "test_download_pdf_data.py",
    ],
)
T(
    "STRONG",
    PDFJS + "browser_pdfjs_force_opening_files.js; browser_pdfjs_not_default.js; "
    "browser_pdfjs_octet_stream.js; " + APP + "browser_pdf_disabled.js",
    "Whether a PDF opens in the built-in viewer or is handed to the download flow, including the "
    "Content-Disposition: attachment case and the Always Ask handler setting.",
    [
        P + "test_open_pdf_in_FF.py",
        P + "test_download_triggered_on_content_disposition_attachment.py",
    ],
)
T(
    "STRONG",
    PDFJS + "browser_pdfjs_form.js; browser_pdfjs_unload_dialog.js",
    "test_defaults fills an AcroForm and asserts the values stick; the unload-dialog tests cover "
    "the prompt when leaving with unsaved data, which is the 'data can be cleared' path.",
    [P + "test_pdf_data_can_be_cleared.py"],
)
T(
    "STRONG",
    PDFJS + "browser_pdfjs_editing_contextmenu.js; browser_pdfjs_editing_telemetry.js",
    "test_copy_paste_undo_redo covers copy and paste of editor content by keyboard and context "
    "menu.",
    [
        P + "test_pdf_copy_paste_functionality.py",
        P + "test_pdf_copy_paste_functionality_numerical.py",
    ],
)

# ================================================================ sidebar
T(
    "STRONG",
    SB + "browser_hide_sidebar.js; browser_hide_sidebar_on_popup.js; "
    "browser_sidebar_escape_collapse.js; browser_launcher_hidden_restore.js",
    "Hiding and restoring the sidebar, including the collapse-on-Escape path.",
    [S + "test_hide_sidebar_behaviour.py"],
)
T(
    "STRONG",
    SB + "browser_toolbar_sidebar_button.js; browser_sidebar_menubar_item_commands.js; "
    "browser_sidebar_macmenu.js",
    "The toolbar button that toggles the sidebar.",
    [S + "test_toggle_sidebar_via_toolbar_button.py"],
)
T(
    "STRONG",
    SB + "browser_sidebar_expand_on_hover.js; browser_sidebar_position.js; "
    "browser_resize_sidebar.js; browser_sidebar_max_width.js",
    "browser_sidebar_expand_on_hover.js covers expand-on-hover, and browser_sidebar_position.js "
    "the left/right placement -- the two halves of the 'unaffected by right-side position' case.",
    [
        S
        + "test_sidebar_expand_collapse_on_hover_unaffected_by_right_side_position.py",
        S + "test_switching_to_horizontal_tabs_disables_expand_on_hover.py",
    ],
)
T(
    "STRONG",
    SB + "browser_customize_sidebar.js; browser_extensions_sidebar.js; "
    "browser_sidebar_prefs.js",
    "Managing which extensions are pinned to the sidebar is covered by the customize and "
    "extensions tests.",
    [S + "test_user_can_manage_pinned_extensions_on_the_sidebar.py"],
)
T(
    "STRONG",
    GENAI
    + "browser_chat_sidebar.js; browser_chat_contextmenu.js; browser_chat_prompt.js; "
    "browser_chat_shortcuts.js; browser_chat_page.js",
    "browser_chat_contextmenu.js drives the AI chat entry points from the page and tab context "
    "menus, and browser_chat_prompt.js the summarize-style prompts -- which is what these five "
    "STARfox tests walk.",
    [
        S + "test_choose_ai_chatbot_via_page_context_menu.py",
        S + "test_open_ai_chat_via_context_menu.py",
        S + "test_summarize_page_via_ai_chat_panel.py",
        S + "test_summarize_page_via_sidebar_ai_chat_context_menu.py",
        S + "test_summarize_page_via_tab_context_menu.py",
    ],
)
T(
    "STRONG",
    GENAI
    + "browser_chat_sidebar.js; browser_chat_nimbus.js; "
    + SB
    + "browser_customize_sidebar.js",
    "Removing the AI chatbot from the sidebar and the resulting absence of its context-menu "
    "entry.",
    [S + "test_ai_chatbot_removed_from_sidebar_not_shown_in_tab_context_menu.py"],
)
T(
    "STRONG",
    SB + "browser_sidebar_prefs.js; browser_sidebar_panel_states.js; "
    "browser/components/privatebrowsing/test/browser/browser_privatebrowsing_sidebar.js",
    "The sidebar's availability and state in a private window.",
    [S + "test_sidebar_enabled_in_private_window.py"],
)

# ================================================================ partial / unique
T(
    "PARTIAL",
    SB + "browser_opentabs_sidebar.js; browser_opentabs_hover_preview.js; "
    "browser_sidebar_collapsed_close_tab_button.js",
    "browser_opentabs_sidebar.js covers the open-tabs panel listing and "
    "browser_sidebar_collapsed_close_tab_button.js the close button on a collapsed row, so the "
    "close-on-hover case is partly covered -- but the tree has no equivalent for the rest of the "
    "vertical-tabs interaction set.",
    [S + "test_close_button_present_on_hovering_or_selecting_a_vertical_tab.py"],
)
T(
    "UNIQUE",
    SB + "browser_opentabs_sidebar.js",
    "Vertical tabs as a tab strip -- duplicating a row, reloading one, bookmarking it, muting it, "
    "its close and move submenus, multi-select and multi-select close, reopening a closed "
    "vertical tab, pinning with expand-on-hover on, and switching between horizontal and "
    "vertical layouts. The tree's sidebar tests treat open-tabs as a read-only list panel; none "
    "of these interactions has an in-tree counterpart. This is the largest block of genuinely "
    "unique STARfox coverage in the round.",
    [
        S + "test_sidebar_duplicate_vertical_tab.py",
        S + "test_sidebar_vertical_tab_can_be_reloaded.py",
        S + "test_sidebar_vertical_tabs_bookmarked.py",
        S + "test_sidebar_vertical_tabs_closing_options.py",
        S + "test_sidebar_vertical_tabs_move_options.py",
        S + "test_sidebar_vertical_tabs_multiselect_close_options.py",
        S + "test_sidebar_vertical_tabs_mute_unmute.py",
        S + "test_sidebar_multiple_vertical_tabs_selection.py",
        S + "test_vertical_tabs_reopen_closed_tab.py",
        S + "test_vertical_tab_pinned_unpinned_with_expand_on_hover_enabled.py",
        S + "test_switch_between_horizontal_vertical_tabs.py",
    ],
)
T(
    "UNIQUE",
    PDFJS + "browser_pdfjs_form.js",
    "AcroForm *interaction*: typing into text and numeric fields, editing pre-filled values, "
    "modifying existing data, dropdown menus, checkboxes, and zoom behaviour inside form fields "
    "and dropdowns. browser_pdfjs_form.js only asserts the form is enabled and fillable at all; "
    "the per-widget behaviour lives upstream in mozilla/pdf.js, so within the tree under "
    "comparison these are STARfox's own coverage.",
    [
        P + "test_pdf_input_numbers.py",
        P + "test_pdf_prefilled_input_data.py",
        P + "test_pdf_modify_text_number_data.py",
        P + "test_pdf_dropdown_functionality.py",
        P + "test_pdf_checkbox_functionality.py",
        P + "test_pdf_zoom_in_text_fields.py",
        P + "test_pdf_zoom_checkboxes.py",
        P + "test_zoom_works_on_dropdown_menus.py",
    ],
)
T(
    "PARTIAL",
    PDFJS + "browser_pdfjs_editing_contextmenu.js; browser_pdfjs_stamp_telemetry.js; "
    "browser_pdfjs_editing_telemetry.js",
    "The editor toolbar's Text and Draw buttons, and adding an image, are only reachable in tree "
    "through the telemetry probes and the context-menu test; the editor interactions themselves "
    "are upstream.",
    [
        P + "test_pdf_text_and_draw_toolbar_buttons.py",
        P + "test_add_image_pdf.py",
    ],
)
T(
    "PARTIAL",
    DL + "browser_downloads_panel_opens.js; browser_first_download_panel.js; "
    "browser_downloads_panel_dontshow.js",
    "The downloads panel opening behaviour is well covered, but the Glean download telemetry "
    "these five STARfox tests assert -- the events recorded when the panel opens, when a download "
    "completes, and when one is opened afterwards -- has no in-tree probe test.",
    [
        D + "test_download_telemetry_recorded.py",
        D + "test_no_download_telemetry_without_panel.py",
        D + "test_telemetry_download_and_open.py",
        D + "test_telemetry_pdf_download_open.py",
        D + "test_verify_telemetry_downloads_panel_open.py",
    ],
)
T(
    "PARTIAL",
    "browser/components/tests/browser/browser_quit_multiple_tabs.js; "
    + DL
    + "browser_downloads_pauseResume.js",
    "The quit-confirmation prompt is covered generally, but not the specific variant raised when "
    "a download is still in progress.",
    [D + "test_close_browser_with_download_in_progress_shows_prompt.py"],
)
T(
    "PARTIAL",
    "toolkit/mozapps/extensions/test/xpcshell/test_signed_verify.js; "
    "toolkit/mozapps/extensions/test/xpcshell/test_signed_install.js",
    "Add-on signature enforcement is covered at the xpcshell level, but not the browser-level "
    "flow of downloading an unsigned add-on and being refused the install.",
    [D + "test_install_unsigned_addons.py"],
)
