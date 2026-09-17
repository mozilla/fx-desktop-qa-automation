"""Critical round -- Printing (suite 73) and Find in page / PDF viewer (suite 65),
plus the printing and PDF sections of the 71226 release smoke matrix.

Two caveats shape the verdicts here:

* toolkit/components/printing/tests asserts the *settings handed to the printer* and the
  print-preview UI state, not ink on paper. That is a genuine match for "can the user change
  X and does it reach the printer", but not for "does the output look right", which is what
  most of suite 73 section 50780 is really asking.

* pdf.js lives upstream in mozilla/pdf.js. toolkit/components/pdfjs/test only covers the
  *integration* layer -- the viewer loading, the findbar, forms, save-as, printing, context
  menus and the telemetry probes. The page-organize, merge, signature, image and alt-text
  editors are tested upstream, outside the tree this comparison is scoped to, so they are
  kept rather than de-prioritised.
"""

from _ledger import C

PRINT = "toolkit/components/printing/tests/"
PDFJS = "toolkit/components/pdfjs/test/"

# ================================================================ suite 73: print dialog
C(
    73,
    "STRONG",
    PRINT + "browser_modal_print.js; browser_print_page_size.js",
    "testPageSizePortrait, testPageSizeLandscape, testFirstPageSizePortrait, "
    "testFirstPageSizeLandscape and testEnterPrintsFromOrientation drive the orientation "
    "control; testLandscapePageSizePassedToPrinter asserts the choice reaches the printer "
    "settings.",
    [965143, 38238, 38239],
)
C(
    73,
    "STRONG",
    PRINT + "browser_destination_change.js; browser_destination_sort.js",
    "Changing the print destination and the ordering of the destination list are covered by "
    "two dedicated tests.",
    [965144],
)
C(
    73,
    "STRONG",
    PRINT + "browser_print_page_range.js",
    "Covers both the custom page range and the non-contiguous range syntax, asserting the "
    "resulting range reaches the printer.",
    [965146, 1081124],
)
C(
    73,
    "STRONG",
    PRINT
    + "browser_print_paper_sizes.js; browser_empty_paper_sizes.js; browser_print_page_size.js",
    "testCustomPageSizePassedToPrinter, testNamedPageSizePassedToPrinter and the paper-size "
    "list tests cover changing paper size, including the degenerate empty/zero-size cases.",
    [965148],
)
C(
    73,
    "STRONG",
    PRINT + "browser_print_scaling.js",
    "Page scale, both the preset percentages and fit-to-page.",
    [965149],
)
C(
    73,
    "STRONG",
    PRINT + "browser_print_margins.js",
    "Custom margin entry and the resulting margin settings.",
    [965248],
)
C(
    73,
    "STRONG",
    PRINT + "browser_modal_print.js; browser_preview_tab_unload.js",
    "testPrintMultiple opens the print modal from several tabs and "
    "testPrintOnNewWindowDoesntClose covers the multi-window case.",
    [966822],
)
C(
    73,
    "STRONG",
    PRINT + "browser_modal_print.js",
    "testTabOrder walks the modal by keyboard, and testEnterAfterLoadPrints, "
    "testEnterPrintsFromPageRangeSelect and testEnterPrintsFromOrientation each complete a "
    "print without touching the mouse.",
    [975705],
)
C(
    73,
    "STRONG",
    PRINT + "browser_modal_resize.js",
    "Resizes the window and asserts the print preview reflows rather than clipping.",
    [975799],
)
C(
    73,
    "STRONG",
    PRINT + "browser_print_selection.js",
    "print_selection, no_print_selection, print_selection_switch and "
    "open_system_print_with_selection_and_pdf cover printing a selection, including through "
    "the system dialog.",
    [1048656],
)
C(
    73,
    "STRONG",
    PRINT + "browser_print_duplex.js",
    "Duplex / both-sides printing option.",
    [1081123, 39687],
)
C(
    73,
    "STRONG",
    PRINT + "browser_print_simplified_mode.js",
    "The Simplified page format toggle and the simplified content that is sent to print.",
    [1490608],
)
C(
    73,
    "STRONG",
    PRINT
    + "browser_print_frame.js; browser_print_pdf_on_frame_load.js; browser_print_coop.js",
    "Printing a page containing frames, including the cross-origin-isolated variant.",
    [38235],
)
C(
    73,
    "STRONG",
    PRINT
    + "browser_pdf_printer_settings.js; browser_print_stream.js; "
    + PDFJS
    + "browser_pdfjs_print_enabled.js",
    "testPDFFile and testPDFPrinterSettings print a real PDF through the Print to PDF "
    "destination; browser_print_stream.js asserts the emitted stream.",
    [38244, 38250, 3248864],
)

# ================================================================ suite 65: PDF forms + viewer
C(
    65,
    "STRONG",
    PDFJS + "browser_pdfjs_form.js; browser_pdfjs_saveas.js",
    "test_defaults fills an AcroForm and asserts the values stick; test_pdf_saveas_forms "
    "saves the filled document and re-reads the field values.",
    [1017484, 3248875],
)
C(
    65,
    "STRONG",
    PDFJS + "browser_pdfjs_unload_dialog.js",
    "test_save_dialog_when_leaving_unsaved_form, test_dontsave_dialog_when_leaving_unsaved_form "
    "and test_cancel_dialog_when_leaving_unsaved_form cover the 'save data before leaving' "
    "prompt and all three of its outcomes.",
    [1020328],
)
C(
    65,
    "STRONG",
    PDFJS + "browser_pdfjs_saveas.js",
    "test_pdf_saveas_forms asserts a saved copy retains the entered form data; "
    "test_pdf_saveas_customname covers the filename path.",
    [1048657],
)
C(
    65,
    "STRONG",
    PDFJS
    + "browser_pdfjs_download_button.js; browser_pdfjs_savedialog.js; browser_pdfjs_saveas.js",
    "Downloading the open PDF through the viewer's download button, with the form data "
    "preserved in the written file.",
    [1020329],
)
C(
    65,
    "STRONG",
    PDFJS + "browser_pdfjs_zoom.js",
    "test and test_browser_zoom step through the viewer's predefined zoom levels and the "
    "browser-level zoom interaction.",
    [3929],
)
C(
    65,
    "STRONG",
    PDFJS
    + "browser_pdfjs_print_enabled.js; "
    + PRINT
    + "browser_pdf_printer_settings.js",
    "test_print_enabled / test_print_disabled drive printing from the pdf.js toolbar.",
    [3931],
)
C(
    65,
    "STRONG",
    PDFJS + "browser_pdfjs_find.js",
    "test_findbar_in_pdf, test_findbar_in_pdf_with_notfound_sound, "
    "test_findbar_in_pdf_with_wrapped_sound, test_findbar_after_navigate and "
    "test_findbar_in_pdf_after_adopt cover phrase search in a PDF including the not-found and "
    "wrap-around states.",
    [1724944],
)
C(
    65,
    "STRONG",
    PDFJS + "browser_pdfjs_editing_contextmenu.js",
    "test_copy_paste_undo_redo copies, cuts and pastes an editor annotation via both the "
    "keyboard shortcuts and the context menu, with undo/redo -- covering the text-area and "
    "drawing-area variants of these four cases.",
    [1938270, 1938271, 1938263, 1938264, 3248876],
)
C(
    65,
    "STRONG",
    PDFJS
    + "browser_pdfjs_editing_contextmenu.js; browser_pdfjs_highlight_telemetry.js",
    "test_highlight_selection creates a highlight over selected text and removes it again.",
    [2741657, 2741658],
)
C(
    65,
    "STRONG",
    PDFJS + "browser_pdfjs_editing_contextmenu.js; browser_pdfjs_comment.js; "
    "browser_pdfjs_comment_telemetry.js",
    "test_comment_selection adds a comment from a text selection; the comment tests cover the "
    "in-content entry point and the resulting comment state.",
    [3136668, 3139940],
)
C(
    65,
    "STRONG",
    PDFJS + "browser_pdfjs_saveas.js; browser_pdfjs_editing_telemetry.js",
    "test_pdf_saveas writes the edited document and the saved bytes are re-parsed, so added "
    "text and drawing annotations are asserted to persist into the saved file.",
    [1938267, 1938260],
)

# ================================================================ reviewed but kept
C(
    73,
    "MEDIUM",
    PRINT + "browser_preview_more_settings.js",
    "moreSettingsHonorPref only checks the disclosure state of the More Settings section. "
    "Colour mode and pages-per-sheet are not individually asserted.",
    [965147, 965247],
)
C(
    73,
    "MEDIUM",
    PRINT + "browser_ui_labels.js",
    "test_FormFieldLabels checks the modal's form labels, which is a piece of the picture, but "
    "not a screen-reader walk of every element.",
    [1234117],
)
C(
    73,
    "MEDIUM",
    PRINT + "browser_print_stream.js",
    "Print-output fidelity rows: various document formats, HTML widgets, image formats, text "
    "files, HTML files, non-Latin locales, Reader View pages and RTL documents. The tree "
    "asserts the settings and the stream, never the rendered page, which is the whole point of "
    "these cases.",
    [
        38236,
        38240,
        38241,
        38242,
        38243,
        131332,
        423757,
        423758,
        3248861,
        3248862,
        3248863,
    ],
)
C(
    73,
    "MEDIUM",
    PRINT + "browser_print_in_container.js; browser_preview_in_container.js",
    "Container-tab printing is covered; private-window printing specifically is not.",
    [423760],
)
C(
    73,
    "MEDIUM",
    PRINT + "browser_print_stream.js",
    "Content-specific print fidelity: wide elements, per-site-type layouts, HTML image maps, "
    "webmail and generated HTML documents. Same limitation -- no rendered-output assertion.",
    [1493917, 1493921, 1507430, 1507431, 1507434],
)
C(
    65,
    "MEDIUM",
    PDFJS + "browser_pdfjs_pages_contextmenu.js; browser_pdfjs_organize_telemetry.js",
    "test_pages_context_menu covers the page context menu existing and its telemetry, but the "
    "page-organize editor itself -- drag to reorder, multi-select, copy/cut/delete pages, "
    "save-as of a reordered document, large and password-protected PDFs, the NEW badge -- is "
    "tested upstream in mozilla/pdf.js, not in this tree.",
    [
        3969287,
        3969288,
        3969289,
        3969290,
        3969291,
        3969292,
        3969293,
        3969294,
        3969295,
        3969296,
        3969297,
        3969298,
        3969299,
        3969300,
        3969301,
        3969302,
    ],
)
C(
    65,
    "MEDIUM",
    PDFJS + "browser_pdfjs_pages_contextmenu.js; browser_pdfjs_hcm.js",
    "The accessibility and theme matrix over page-organize and PDF merging (keyboard access to "
    "the Manage dropdown, screen readers, HCM, light and dark mode). browser_pdfjs_hcm.js "
    "covers HCM rendering of the viewer only.",
    [
        3969277,
        3969278,
        3969279,
        3969280,
        3969281,
        3969282,
        3969283,
        3969284,
        3969285,
        3969286,
        3969304,
        3969305,
        3969306,
        4027170,
        4027171,
        4027172,
        4027173,
        4027174,
    ],
)
C(
    65,
    "MEDIUM",
    PDFJS + "browser_pdfjs_saveas.js",
    "PDF merging -- adding files to an open document, landscape/portrait handling, export of "
    "selected pages, progress for very large files, drag-and-drop into the sidebar, and "
    "re-opening the result in other viewers. Upstream pdf.js territory.",
    [
        4027159,
        4027160,
        4027161,
        4027162,
        4027163,
        4027164,
        4027165,
        4027166,
        4027167,
        4027168,
        4027169,
    ],
)
C(
    65,
    "MEDIUM",
    PDFJS + "browser_pdfjs_form.js; browser_pdfjs_hcm.js",
    "Form rows beyond basic entry: keyboard navigation within the form, High Contrast input, "
    "drag-and-drop of text into fields, and whether filled text, checkboxes, radio buttons and "
    "dropdown selections come out correctly on the printed page.",
    [1017608, 1018198, 1018209, 1018210, 1018211, 1018212, 1020331],
)
C(
    65,
    "MEDIUM",
    PDFJS + "browser_pdfjs_editing_telemetry.js; browser_pdfjs_zoom.js",
    "Editor behaviour the integration layer does not reach: placing and resizing text areas, "
    "the Hand Tool interaction, editing in private browsing and High Contrast, zooming an "
    "edited document, searchability and screen-reader access of a saved edited PDF, printing "
    "the annotations, and large-document save/print performance.",
    [
        1938265,
        1938266,
        1938268,
        1938272,
        1938273,
        1938255,
        1938256,
        1938257,
        1938258,
        1938261,
        1995496,
        3248878,
        3248879,
    ],
)
C(
    65,
    "MEDIUM",
    PDFJS + "browser_pdfjs_highlight_telemetry.js",
    "Highlighting an image inside a scanned PDF and freehand highlight over mixed text and "
    "image content -- neither is exercised by the in-tree integration tests.",
    [4038756, 4038757],
)
C(
    65,
    "MEDIUM",
    PDFJS + "browser_pdfjs_signature_storage.js; browser_pdfjs_signature_telemetry.js; "
    "browser_pdfjs_digital_signature_properties.js",
    "Signature storage and telemetry are covered, but not the three-tab (Type / Draw / Image) "
    "editor behaviour, editing a saved typed signature, or printing a signed document.",
    [2913009, 2914745, 2914782],
)
C(
    65,
    "MEDIUM",
    PDFJS + "browser_pdfjs_alttext_load_engine.js; browser_pdfjs_alttext_telemetry.js; "
    "browser_pdfjs_alttext_two_tabs.js; browser_pdfjs_stamp_telemetry.js",
    "The alt-text engine loading and its telemetry are covered; generating alt text for an "
    "added image and then editing it, and resizing / multi-image save, are not.",
    [2741745, 2741746, 2228230, 2228309],
)
C(
    65,
    "MEDIUM",
    PDFJS + "browser_pdfjs_force_opening_files.js; browser_pdfjs_not_default.js",
    "Handing the PDF off to a third-party desktop application depends on an external handler "
    "being installed and is not reachable from the browser-chrome harness.",
    [3936, 3248882],
)
C(
    65,
    "MEDIUM",
    PDFJS + "browser_pdfjs_comment.js; browser_pdfjs_comment_telemetry.js",
    "Editing, deleting and saving a comment attached to a paragraph, and the responsiveness of "
    "the comment sidebar, go beyond test_learn_more_url and the comment telemetry probes.",
    [3139285, 3139287, 3139289, 3139927],
)
