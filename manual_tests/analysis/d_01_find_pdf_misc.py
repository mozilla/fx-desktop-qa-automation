# Per-case verdicts: manual TestRail cases whose user flow is covered by automated
# tests inside mozilla-firefox/firefox (mozilla-central).
#
# tier:
#   "STRONG" - an in-tree automated test drives the same UI flow and asserts the same
#              user-visible outcome. Safe to de-prioritise for manual crunch-time runs.
#   "MEDIUM" - in-tree test touches the feature but at a narrower scope / lower altitude
#              (pref-only, telemetry-only, one variant of a matrix). Keep in rotation.
# Only STRONG rows are emitted into the low-priority list.
#
# Every "tests" path was checked against a recursive listing of the live tree
# (see .fxtree/) and, where the mapping was not 1:1, against the file contents.

from _ledger import C

# ---------------------------------------------------------------- suite 2085
# "Find Toolbar" (46 cases)
C(
    2085,
    "STRONG",
    "toolkit/content/tests/browser/browser_findbar.js; "
    "toolkit/content/tests/chrome/findbar_window.xhtml; toolkit/content/tests/chrome/test_findbar.xhtml",
    "findbar_window.xhtml drives the real findbar widget end to end: open, normal find, "
    "highlight, match count, links-only, quick find, entire-word, case sensitivity, "
    "not-found status. browser_findbar.js adds hotkeys, per-tab state and state "
    "preservation across reload.",
    [
        127238,  # Find Toolbar can be opened
        127239,  # a search can be performed
        127240,  # found item correctly highlighted
        127451,  # "Highlight All" button
        127452,  # "Match Case" button
        127453,  # "Whole Words" button
        127241,  # number of found items displayed
        127245,  # searching for a non-existent string
        127249,  # navigation through found items
        127258,  # navigation using ENTER
        127259,  # Quick Find
        127260,  # navigation through Quick Find items
        127252,  # searching for Links only
        127253,  # navigation through Links-only results
        127264,  # searching again after navigating to another page
        127265,  # searching on a page with iframe
    ],
)
C(
    2085,
    "STRONG",
    "toolkit/components/pdfjs/test/browser_pdfjs_find.js",
    "Find inside the built-in PDF viewer is driven end to end.",
    [127271],  # searching on a PDF page
)
C(
    2085,
    "MEDIUM",
    "toolkit/content/tests/browser/browser_findbar.js; browser/base/content/test/general/browser_findbarClose.js",
    "Per-tab findbar instances and closing are covered, but 'term kept on new tab, not on "
    "new window' is not asserted directly.",
    [127246, 127256, 127257, 127262, 127263],
)
C(
    2085,
    "MEDIUM",
    "toolkit/content/tests/browser/browser_findbar_marks.js; browser_findbar_hidden_reveal.js; browser_findbar_hidden_beforematch.js",
    "Scroll-marks and hidden/beforematch reveal are automated; the manual cases are about "
    "visual correctness (zoom, dark bg, HCM, small fonts) which the tree checks via reftest at most.",
    [127243, 127266, 127269, 127278],
)

# ---------------------------------------------------------------- suite 65
# "Find in page / PDF" (196 cases) - pdf.js area
C(
    65,
    "STRONG",
    "toolkit/components/pdfjs/test/browser_pdfjs_find.js",
    "Find phrases inside pdf.js.",
    [1724944],
)
C(
    65,
    "STRONG",
    "toolkit/components/pdfjs/test/browser_pdfjs_navigation.js",
    "Page navigation (next/prev/page-number/outline/hash anchors) inside pdf.js.",
    [3927],
)
C(
    65,
    "STRONG",
    "toolkit/components/pdfjs/test/browser_pdfjs_zoom.js",
    "Zoom in/out, predefined zoom levels and browser-level zoom in pdf.js.",
    [3928, 3929],
)
C(
    65,
    "STRONG",
    "toolkit/components/pdfjs/test/browser_pdfjs_download_button.js; browser_pdfjs_saveas.js; browser_pdfjs_savedialog.js",
    "Download / Save-as from the pdf.js toolbar.",
    [3932],
)
C(
    65,
    "STRONG",
    "toolkit/components/pdfjs/test/browser_pdfjs_main.js; browser_pdfjs_not_default.js; browser_pdfjs_response_link.js",
    "pdf.js is the default handler and opens PDFs navigated to from links/urlbar.",
    [193859, 936503],
)
C(
    65,
    "STRONG",
    "toolkit/components/pdfjs/test/browser_pdfjs_fullscreen.js",
    "Presentation / fullscreen mode of the PDF viewer.",
    [3930],
)
C(
    65,
    "MEDIUM",
    "toolkit/components/pdfjs/test/browser_pdfjs_form.js",
    "VERIFIED THIN: the in-tree test only asserts the renderInteractiveForms pref default "
    "and the disabled state - it never fills a field. The ~45 PDF form-field manual cases "
    "are covered upstream in github.com/mozilla/pdf.js, NOT in mozilla-central.",
    [1017484, 1017488, 1017491, 1017528, 1019456, 1020324, 1020330],
)
C(
    65,
    "MEDIUM",
    "toolkit/components/pdfjs/test/browser_pdfjs_comment.js; browser_pdfjs_comment_telemetry.js",
    "VERIFIED THIN: browser_pdfjs_comment.js only checks the 'learn more' URL when a PDF has "
    "no comments. The ~45 manual PDF-commenting cases have no equivalent in-tree.",
    [3136664, 3136668, 3139940],
)
C(
    65,
    "MEDIUM",
    "toolkit/components/pdfjs/test/browser_pdfjs_pages_contextmenu.js; browser_pdfjs_organize_telemetry.js",
    "Page organise context menu (copy/cut/delete/save-as) is automated; drag-reorder, merge "
    "and the a11y/theme matrix are not.",
    [3969283, 3969277, 3969278, 3969282, 3969291],
)
C(
    65,
    "MEDIUM",
    "toolkit/components/pdfjs/test/browser_pdfjs_editing_contextmenu.js; browser_pdfjs_highlight_telemetry.js; "
    "browser_pdfjs_stamp_telemetry.js; browser_pdfjs_signature_storage.js; browser_pdfjs_digital_signature_properties.js",
    "Editor/highlight/stamp/signature exist in-tree mostly as telemetry or storage tests, "
    "not as full editing UX.",
    [1938254, 2741657, 2228202, 2914782, 2913009],
)
C(
    65,
    "MEDIUM",
    "toolkit/components/pdfjs/test/browser_pdfjs_octet_stream.js; browser_pdfjs_force_opening_files.js; browser_pdfjs_not_default.js",
    "Content-disposition / 'always ask' / external-handler paths are partially covered.",
    [936502, 3936, 936466, 3934, 504101],
)

# ---------------------------------------------------------------- suite 2126
# "Reader View" (8 cases)
C(
    2126,
    "STRONG",
    "toolkit/components/reader/tests/browser/browser_readerMode.js; browser_readerMode_menu.js",
    "Entering/leaving reader mode from the urlbar button is the core of browser_readerMode.js.",
    [130908],
)
C(
    2126,
    "STRONG",
    "toolkit/components/reader/tests/browser/browser_readerMode_textLayoutPref.js; "
    "browser_readerMode_colorSchemePref.js; browser_readerMode_customColorScheme.js",
    "The type/appearance controls panel (font, size, spacing, width, colour scheme) is "
    "automated across three dedicated tests.",
    [130919],
)
C(
    2126,
    "STRONG",
    "toolkit/components/narrate/test/browser_narrate.js; browser_narrate_toggle.js; "
    "browser_narrate_language.js; browser_voiceselect.js; browser_word_highlight.js",
    "The narrate panel and its settings (voice, rate, language, word highlight) have a "
    "dedicated in-tree browser-chrome suite.",
    [130918, 130923],
)
C(
    2126,
    "MEDIUM",
    "toolkit/components/reader/tests/browser/browser_readerMode_tabnavigation.js; "
    "browser_bug1124271_readerModePinnedTab.js; browser_bug1780350_readerModeSaveScroll.js",
    "Tab navigation / pinned-tab reuse / scroll save are automated; 'basic interaction with "
    "browser functions', sidebar close and bookmark/history/sync availability are not.",
    [130929, 130912, 466776],
)

# ---------------------------------------------------------------- suite 498
# "Geolocation" (6 cases)
C(
    498,
    "STRONG",
    "dom/geolocation/test/browser/browser_geolocation_override.js; browser_bug1008941_dismissGeolocationHanger.js; "
    "browser/base/content/test/siteIdentity/browser_geolocation_indicator.js; "
    "browser/base/content/test/permissions/browser_geolocation_replaced_prompt.js",
    "Prompt, grant/dismiss, position delivery to the page and the sharing indicator are all "
    "automated; the W3C/HTML5 API distinction is the same code path.",
    [15186, 15189],
)
C(
    498,
    "MEDIUM",
    "dom/geolocation/test/browser/browser_bug1238427.js",
    "Request timeout behaviour is touched; API-key and real-site checks are manual by nature.",
    [100045],
)

# ---------------------------------------------------------------- suite 73783
# "Reduced Protection (PBM/ETP)" (13 cases)
C(
    73783,
    "STRONG",
    "browser/modules/test/browser/browser_ReducedProtectionNotification.js; "
    "browser_ReducedProtectionNotification_permanentPB.js",
    "The reduced-protection infobar is driven directly: shown in PBM, per-site/per-tab "
    "suppression, dismissal, and the resulting pref state.",
    [3334630, 3334633, 3334721, 3486452, 3334722, 3334862, 3493474],
)
C(
    73783,
    "MEDIUM",
    "browser/base/content/test/protectionsUI/browser_protectionsUI.js",
    "ETP strict/custom interaction with the notification is only indirectly covered; "
    "HCM/theme/screen-reader variants are not automated at all.",
    [3334631, 3334632, 3334863],
)

# ---------------------------------------------------------------- suite 100547
# "Private Window appearance (NOVA)" (17 cases) - visual redesign suite
C(
    100547,
    "MEDIUM",
    "browser/components/privatebrowsing/test/browser/browser_privatebrowsing_theming.js; "
    "browser_privatebrowsing_ui.js; browser_privatebrowsing_about_nova_promo.js; browser_privatebrowsing_sidebar.js",
    "Private-window chrome/theming and the sidebar are automated behaviourally, but this "
    "suite is a visual-redesign (NOVA) suite - layout/badge/appearance assertions have no "
    "in-tree analog.",
    [4037345, 4037346, 4038415, 4038417, 4038418, 4038419, 4038420],
)

# ---------------------------------------------------------------- suite 70723
# "Rename tabs" (30 cases)
C(
    70723,
    "STRONG",
    "browser/components/tabnotes/test/browser/browser_tab_notes_menu.js; browser_tab_notes_navigation.js; "
    "browser_tab_notes_adopt.js; browser_tab_notes_enable_disable.js; browser_tab_notes_history_pushstate.js; "
    "browser/components/sessionstore/test/browser_tab_notes_canonicalurl.js; "
    "browser/components/tabbrowser/test/browser/tabs/browser_tab_note_preview.js",
    "The user-generated tab title (tab notes) feature has a dedicated in-tree suite covering "
    "the context-menu entry, persistence across navigation/pushstate, window adopt, session "
    "restore and the hover preview.",
    [
        3228304,  # rename via context menu
        3228306,  # name kept when loading a different address
        3228317,  # UG title in tab hover preview
        3228311,  # UG title + note on tab restore
        3228313,  # UG title retained after session restore
        3228312,  # UG title not drawn from History
    ],
)
C(
    70723,
    "MEDIUM",
    "browser/components/tabbrowser/test/browser/tabs/browser_tab_label_character_cap.js",
    "Tab-label capping exists; double-click rename, editing affordances, undo/redo, empty "
    "entry, duplicate names and the a11y flows are not automated in-tree.",
    [3228303, 3228688, 3228543, 3228318],
)