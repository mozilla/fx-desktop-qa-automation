from _ledger import C, CSEC

# ---------------------------------------------------------------- suite 29219
# "Downloads" (224 cases). Tree: browser/components/downloads/test/browser/ (39),
# uriloader/exthandler/tests/mochitest/browser_*.js (21),
# browser/components/preferences/tests/{downloads,applications}/ (17).
C(
    29219,
    "STRONG",
    "browser/components/downloads/test/browser/browser_basic_functionality.js; "
    "browser_downloads_panel_opens.js; browser_first_download_panel.js; browser_downloads_panel_dontshow.js; "
    "browser_downloads_panel_height.js; browser_overflow_anchor.js",
    "The panel auto-opening on the first download, not re-opening while another download is in "
    "progress, and basic panel population.",
    [1756750, 1756751],
)
C(
    29219,
    "STRONG",
    "browser/components/downloads/test/browser/browser_downloads_panel_context_menu.js; "
    "browser_downloads_context_menu_selection.js; browser_downloads_context_menu_delete_file.js; "
    "browser_downloads_context_menu_always_open_similar_files.js; browser_downloads_panel_disable_items.js; "
    "browser_downloads_panel_ctrl_click.js",
    "The download item context menu: copy download link, delete file, 'always open similar files', "
    "and which items are enabled per state.",
    [1756901, 1756714, 1756764, 1756753],
)
C(
    29219,
    "STRONG",
    "browser/components/downloads/test/browser/browser_downloads_pauseResume.js; browser_download_failed_msg.js; "
    "browser_downloads_context_menu_delete_file.js",
    "Cancel / retry a download and delete one while it is running or paused.",
    [1756701, 1756765, 1756766],
)
C(
    29219,
    "STRONG",
    "browser/components/downloads/test/browser/browser_blocked_and_deleted_status.js; "
    "browser_downloads_panel_block.js; browser_confirm_unblock_download.js; browser_download_spam_protection.js",
    "The malicious / potentially-unwanted / uncommon warning states, the unblock confirmation, "
    "the 'file was deleted' state and configuring the warnings.",
    [1756697, 1756698, 1756699, 1756708, 1756762, 1756692],
)
C(
    29219,
    "STRONG",
    "browser/components/downloads/test/browser/browser_about_downloads.js; browser_library_clearall.js; "
    "browser_library_select_all.js; browser_go_to_download_page.js",
    "about:downloads contents, Clear Downloads / clear history, select-all and go-to-download-page.",
    [1756694, 1756709, 1756707],
)
C(
    29219,
    "STRONG",
    "browser/components/downloads/test/browser/browser_indicatorDrop.js; browser_libraryDrop.js",
    "Starting a download by dropping a link on the downloads indicator or the Library.",
    [1756703],
)
C(
    29219,
    "STRONG",
    "browser/components/downloads/test/browser/browser_downloads_keynav.js; browser_downloads_panel_focus.js",
    "Keyboard navigation and focus ring inside the downloads panel.",
    [1863803],
)
C(
    29219,
    "STRONG",
    "browser/components/downloads/test/browser/browser_download_is_clickable.js; "
    "browser_download_opens_on_click.js; browser_download_opens_policy.js",
    "Clicking a download entry before it has finished, and opening a finished one.",
    [1756760],
)
C(
    29219,
    "STRONG",
    "uriloader/exthandler/tests/mochitest/browser_download_privatebrowsing.js; "
    "browser/components/downloads/test/browser/browser_download_starts_in_tmp.js",
    "Private-window downloads are not visible from normal browsing, including the "
    "launch-with-application path.",
    [1756758, 1756759],
)
C(
    29219,
    "STRONG",
    "uriloader/exthandler/tests/mochitest/browser_download_always_ask_preferred_app.js; "
    "browser_download_preferred_action.js; browser_download_skips_dialog.js; "
    "browser_download_open_with_internal_handler.js; browser_launched_app_save_directory.js; "
    "browser/components/preferences/tests/applications/browser_filetype_dialog.js; browser_change_app_handler.js",
    "'Always ask' for a file type, choosing 'Use another application', and where a "
    "launched-with-application file is saved.",
    [1756752, 4108462, 1756754, 1756757],
)
C(
    29219,
    "STRONG",
    "browser/components/preferences/tests/downloads/browser_downloads.js; "
    "browser_bug1547020_lockedDownloadDir.js; browser_open_download_preferences.js",
    "Changing the download folder from about:preferences.",
    [1756713],
)
C(
    29219,
    "STRONG",
    "uriloader/exthandler/tests/mochitest/browser_download_force_save_attachments.js; "
    "toolkit/components/pdfjs/test/browser_pdfjs_octet_stream.js; browser_pdfjs_download_button.js; "
    "browser/components/downloads/test/browser/browser_pdfjs_preview.js",
    "Downloading a PDF, and the Content-Disposition attachment vs inline paths.",
    [1756769, 1756773, 1756774],
)
# --- The file-type / handler matrix.
CSEC(
    29219,
    "STRONG",
    "browser/components/preferences/tests/applications/browser_applications_selection.js; "
    "browser_change_app_handler.js; browser_filetype_dialog.js; browser_applications_filter.js; "
    "browser_applications_search_results.js; browser_application_xml_handle_internally.js; "
    "browser/components/preferences/tests/downloads/browser_downloads_handle_new_file_types.js; "
    "uriloader/exthandler/tests/mochitest/browser_download_preferred_action.js; browser_extension_correction.js",
    "MATRIX: section 284144 is the same single mechanic - 'add a handler for extension X in the "
    "Applications list and download a file of that type' - repeated once per file extension. The "
    "mechanic (add/change/filter/search a handler, persist the preferred action, apply it on "
    "download) is fully automated in-tree. Recommendation: keep 2-3 representative extensions "
    "(one executable, one archive, one media) in the crunch-time run and de-prioritise the rest.",
    [284144],
)
C(
    29219,
    "STRONG",
    "browser/components/preferences/tests/downloads/browser_downloads_handle_new_file_types.js; "
    "uriloader/exthandler/tests/mochitest/browser_download_preferred_action.js; "
    "browser/components/preferences/tests/applications/browser_applications_selection.js",
    "Same mechanic as the matrix above, for the mime-type rows that live in section 284142.",
    [1756736, 1756737, 1756738, 1756739, 1756740, 1756741, 1756742, 1756743,
     4108460, 1756744, 1756745, 1756746, 1756747, 1756748, 4108461, 1756749],
)
C(
    29219,
    "MEDIUM",
    "browser/components/downloads/test/browser/browser_downloads_taskbar.js; browser_downloads_autohide.js; "
    "browser_download_overwrite.js; browser_tempfilename.js; browser_bad_download_dir.js; "
    "browser_image_mimetype_issues.js; browser_downloads_jsonview.js; "
    "uriloader/exthandler/tests/mochitest/browser_extension_correction.js; browser_auto_close_window.js",
    "Adjacent behaviour is automated, but the manual cases here are about progress-bar/summary "
    "rendering, hover details, OS folder integration, close-while-downloading prompts, the "
    "HTTPS-Only download matrix, real-site file-extension bugs, add-on install from file, "
    "and download telemetry (which STARfox owns, not the tree).",
    [1756702, 1756705, 1756706, 1756711, 1756712, 1756715, 1756704, 1756693,
     1756695, 1756696, 1756755, 1756756, 1756761, 1756763, 1756767, 2091302,
     1855825, 1756768, 1756770, 1756771, 1756772,
     1756722, 1756723, 1756724, 1756725, 1756726, 1756727, 1756728, 1756729,
     1756731, 1756732, 1756733, 1756734,
     1756775, 1756776, 1756777, 1756778, 1756779, 1756780, 1756781, 1756782,
     1756783, 1756784, 1756785, 1756786, 1756787, 1756788, 1756789, 1756790, 1756791,
     1781220, 1781221, 1781223, 1781226,
     1836829, 1836830, 1836831, 1836832],
)
