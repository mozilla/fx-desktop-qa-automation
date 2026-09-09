from _ledger import C, CSEC

# ---------------------------------------------------------------- suite 2525
# "Bookmarks Toolbar" (222 cases - actually bookmarks *and* history/Library).
# Tree: browser/components/places/tests/browser/ (114), .../tests/interactions/ (12),
# toolkit/components/places/tests/browser/, browser/base/content/test/sanitize/ (18),
# browser/components/customizableui/test/browser_{bookmarks,history}_*.js (7).

# --- History menus / sidebar (sections 51064, 51065)
C(
    2525,
    "STRONG",
    "browser/components/places/tests/browser/browser_history_sidebar_search.js; "
    "browser_sidebar_history_telemetry.js; browser_sidebarpanels_click.js; browser_enable_toolbar_sidebar.js; "
    "browser/components/sidebar/tests/browser/browser_history_sidebar.js; browser_history_keyboard_navigation.js; "
    "browser_history_multiselect.js; browser_delete_sidebar_history.js",
    "Opening/closing the History sidebar, searching it (hit, miss, clearing the term), the sort-by "
    "views, and opening an entry from it.",
    [118811, 119440, 119441, 119442, 119443, 119444, 119445, 119446, 119447, 119448, 120116],
)
C(
    2525,
    "STRONG",
    "browser/components/customizableui/test/browser_history_after_appMenu.js; browser_history_recently_closed.js; "
    "browser_history_recently_closed_middleclick.js; browser_history_restore_session.js; "
    "toolkit/components/places/tests/browser/browser_visituri.js",
    "The History submenu in the hamburger/Library menu being populated by recent visits (normal, "
    "new tab, new window) and opening entries from it.",
    [118799, 118800, 118802, 118805, 118807, 178345],
)
C(
    2525,
    "STRONG",
    "browser/components/places/tests/browser/browser_bookmark_private_window.js; "
    "browser/components/privatebrowsing/test/browser/browser_privatebrowsing_placestitle.js; "
    "browser_privatebrowsing_placesTitleNoUpdate.js; browser_privatebrowsing_history_shift_click.js",
    "Private-window visits not appearing in History, and opening a history entry in a private window.",
    [118806, 118808],
)
C(
    2525,
    "STRONG",
    "browser/components/places/tests/browser/browser_forgetthissite.js; browser_library_bookmark_clear_visits.js; "
    "browser/base/content/test/sanitize/browser_sanitize-history.js; browser_purgehistory_clears_sh.js",
    "Deleting a page and 'Forget About This Site' from the sidebar / Library / History menu, and "
    "the deleted-vs-forgotten difference in later urlbar autofill.",
    [120130, 120131, 120132, 120133, 120134, 174048, 174049, 174050, 174051, 174036,
     216273, 178346],
)
C(
    2525,
    "STRONG",
    "browser/components/places/tests/browser/browser_library_middleclick.js; browser_library_open_bookmark.js; "
    "browser_library_open_all.js; browser_library_open_all_with_separator.js; browser_library_openFlatContainer.js; "
    "browser_library_left_pane_middleclick.js; browser_library_warnOnOpen.js; browser_library_commands.js",
    "Opening a history entry from the Library window in the current tab / new tab / new window / "
    "new private window, and opening a whole time range.",
    [174037, 174039, 174040, 174041, 174033],
)
C(
    2525,
    "STRONG",
    "browser/components/places/tests/browser/browser_cutting_bookmarks.js; browser_paste_bookmarks.js; "
    "browser_paste_resets_cut_highlights.js; browser_copy_query_without_tree.js; browser_bookmark_copy_folder_tree.js; "
    "browser_controller_onDrop.js; browser_controller_onDrop_query.js; browser_controller_onDrop_sidebar.js",
    "Copying a history entry or a time-range query from the sidebar / Library and pasting it onto "
    "the Bookmarks Toolbar or into the urlbar.",
    [120125, 120126, 120127, 120128, 120129, 174045, 174047, 174031, 174032, 174034],
)
C(
    2525,
    "STRONG",
    "browser/components/places/tests/browser/browser_bookmarkProperties_editTagContainer.js; "
    "browser_bookmark_add_tags.js; browser_bookmarksProperties.js; browser_bookmark_change_location.js; "
    "browser_library_new_bookmark.js",
    "Bookmarking a page from the History sidebar / Library context menu, including changing its "
    "name, folder and tags in the same step.",
    [120123, 120124, 174042, 174044],
)
C(
    2525,
    "STRONG",
    "browser/components/places/tests/browser/browser_bookmark_context_menu_contents.js; "
    "browser_toolbarbutton_menu_context.js; browser_bookmark_menu_ctrl_click.js",
    "The History sidebar context-menu contents and its open-in-* items.",
    [466771, 120117, 120120, 120121, 120122],
)
CSEC(
    2525,
    "STRONG",
    "browser/base/content/test/sanitize/browser_sanitizeDialog_v2.js; browser_sanitizeDialog_v2_dataSizes.js; "
    "browser_sanitize-timespans.js; browser_sanitize-timespans_v2.js; browser_sanitize-history.js",
    "The Clear Recent History dialog: shown, dismissed, per-time-range clearing, the Clear-now "
    "button disabled with nothing selected, choosing which sections to clear, and clearing all.",
    [51066],
)
C(
    2525,
    "STRONG",
    "browser/base/content/test/sanitize/browser_sanitize-timespans.js; browser_sanitize-timespans_v2.js",
    "The Forget button's 5-minute / 2-hour / 24-hour ranges.",
    [174072, 174073, 174074],
)
# --- Bookmarks proper (sections 400407-400418)
C(
    2525,
    "STRONG",
    "browser/components/places/tests/browser/browser_bookmark_popup.js; browser_bookmarksProperties.js; "
    "browser_bookmarkProperties_newFolder.js; browser_bookmarkProperties_folderSelection.js; "
    "browser_bookmarkProperties_remember_folders.js; browser_bookmarkProperties_cancel.js; "
    "browser_bookmark_add_tags.js; browser_bookmark_remove_tags.js; browser_bookmark_change_location.js; "
    "browser_bookmarks_change_title.js; browser_bookmarks_change_url.js; browser_remove_bookmarks.js; "
    "browser_default_bookmark_location.js",
    "The star button and its Edit-this-bookmark panel: bookmark a page, rename, change folder "
    "(toolbar / menu / other), create a folder inline, add and remove tags, remove the bookmark, "
    "and Cancel.",
    [2084539, 2084540, 2084541, 2084542, 2084543, 2084544, 2084545, 2084546, 2084547,
     2084548, 2084549, 2084643],
)
C(
    2525,
    "STRONG",
    "browser/components/places/tests/browser/browser_bookmarks_toolbar_context_menu_view_options.js; "
    "browser_autoshow_bookmarks_toolbar.js; browser_enable_toolbar_sidebar.js; "
    "browser/components/customizableui/test/browser_bookmarks_toolbar_shown_newtab.js; "
    "browser_bookmarks_toolbar_collapsed_restore_default.js; browser_bookmarks_empty_message.js",
    "Showing/hiding the Bookmarks Toolbar (keyboard shortcut, menu, 'only on new tab'), and the "
    "empty-toolbar message.",
    [2084637, 2084638, 2084645],
)
CSEC(
    2525,
    "STRONG",
    "browser/components/places/tests/browser/browser_click_bookmarks_on_toolbar.js; "
    "browser_drag_bookmarks_on_toolbar.js; browser_toolbar_drop_text.js; browser_toolbar_drop_multiple_flavors.js; "
    "browser_toolbar_drop_indicator_empty.js; browser_toolbar_drop_bookmarklet.js; browser_cutting_bookmarks.js; "
    "browser_paste_bookmarks.js; browser_remove_bookmarks.js; browser_bookmarksProperties.js; "
    "browser_bookmarkProperties_newFolder.js; browser_bookmark_context_menu_contents.js; "
    "browser_bookmark_menu_ctrl_click.js; browser_library_open_all.js; browser_toolbar_overflow.js; "
    "browser_bookmarks_toolbar_drag_with_chevron.js",
    "The Bookmarks Toolbar item set: open (click / new tab / new window / new private window), "
    "New Bookmark, New Folder, New Separator, cut/copy/paste, delete, edit, reorder by drag, add "
    "by drag, Open All, and the overflow chevron.",
    [400411, 400415],
)
CSEC(
    2525,
    "STRONG",
    "browser/components/places/tests/browser/browser_toolbar_other_bookmarks.js; browser_cutting_bookmarks.js; "
    "browser_paste_bookmarks.js; browser_remove_bookmarks.js; browser_bookmarksProperties.js; "
    "browser_bookmarkProperties_newFolder.js; browser_bookmark_menu_ctrl_click.js; "
    "browser_mobile_root_on_bookmark_menus.js; browser_bookmarks_checkDefaultBookmarks.js",
    "The 'Other Bookmarks' and 'Mozilla Firefox' folders: visibility rules, open in tab/window/"
    "private window, add bookmark/folder/separator, cut, copy, delete and edit.",
    [400412, 400413],
)
CSEC(
    2525,
    "STRONG",
    "browser/components/places/tests/browser/browser_bookmarks_sidebar_search.js; browser_sidebar_open_bookmarks.js; "
    "browser_sidebarpanels_click.js; browser_controller_onDrop_sidebar.js; browser_sidebar_bookmarks_telemetry.js; "
    "browser_sidebar_bookmarks_glean.js; browser_sidebar_on_customization.js; browser_bhTooltip_folder_cropping.js; "
    "browser/components/sidebar/tests/browser/browser_bookmarks_sidebar.js; browser_bookmarks_multiselect.js; "
    "browser_bookmarks_keyboard_navigation.js; browser_bookmarks_sidebar_root_folders.js; "
    "browser_bookmarks_show_in_folder_from_menu.js; browser_bookmarks_sidebar_auxclick.js",
    "The Bookmarks Sidebar: enable/disable, search (hit and miss), bookmark by drag-and-drop into "
    "it, open in tab/window/private window, add bookmark/folder/separator, cut/copy/delete/edit, "
    "and reorder by drag.",
    [400416],
)
CSEC(
    2525,
    "STRONG",
    "browser/components/places/tests/browser/browser_library_open_bookmark.js; browser_library_new_bookmark.js; "
    "browser_library_bookmark_move.js; browser_library_bookmark_pages.js; browser_library_delete.js; "
    "browser_library_commands.js; browser_library_search.js; browser_library_middleclick.js; "
    "browser_library_open_all.js; browser_library_open_all_with_separator.js; browser_library_views_liveupdate.js; "
    "browser_library_left_pane_select_hierarchy.js; browser_sort_in_library.js; browser_paste_bookmarks.js; "
    "browser_cutting_bookmarks.js; browser_controller_onDrop.js; browser_bookmark_backup_export_import.js; "
    "browser_bookmark_folder_moveability.js; browser_library_telemetry.js",
    "The Library window for bookmarks: open it, add by drag-and-drop, open an item every way, add "
    "bookmark/folder/separator, delete separators, cut/copy/paste, delete, edit, reorder and move "
    "between sections, and Export / Import bookmarks (HTML backup and from another browser).",
    [400417],
)
C(
    2525,
    "STRONG",
    "browser/components/places/tests/browser/browser_toolbar_library_open_recent.js; "
    "browser_bookmarks_sidebar_search.js; browser_library_search.js; browser_bookmark_add_tags.js; "
    "browser_library_bulk_tag_bookmarks.js; browser_stayopenmenu.js; browser_closePanelview.js; "
    "browser_bookmarks_close_panel.js; browser_panelview_bookmarks_delete.js; "
    "browser_toolbarbutton_menu_show_in_folder.js",
    "The Library toolbar-button Bookmarks submenu: navigation and Back, bookmark/edit the current "
    "page, show/hide the sidebar and toolbar, search (including by tag), and the Recent Bookmarks "
    "list with all its item actions.",
    [2084565, 2084566, 2084567, 2084568, 2084571, 2084573, 2084575, 2084576, 2084577,
     2084578, 2084579, 2084580, 2084581, 2084582, 2084583, 2084584, 2084585, 2084586,
     2091309],
)
C(
    2525,
    "STRONG",
    "browser/components/places/tests/browser/browser_bookmarkProperties_editFolder.js; "
    "browser_bookmarkProperties_addFolderDefaultButton.js; browser_editBookmark_keywords.js; "
    "browser_drag_bookmarks_on_toolbar.js; browser_bookmark_titles.js; browser_recursive_hierarchies.js; "
    "browser_views_liveupdate.js; browser_views_iconsupdate.js",
    "Edit-folder from the toolbar context menu, keywords saved from the Library, reordering by "
    "drag, and live updates of every bookmark view.",
    [2084629, 2084631, 2084632, 2084634, 2084628, 2084644],
)
C(
    2525,
    "STRONG",
    "browser/components/places/tests/browser/browser_import_button.js; browser_bookmark_backup_export_import.js",
    "The Import button on the toolbar: shown/hidden rules and the import flow.",
    [2084646, 2084647, 2084648],
)
C(
    2525,
    "STRONG",
    "browser/components/places/tests/browser/browser_bookmarks_toolbar_telemetry.js; browser_library_telemetry.js; "
    "browser_sidebar_bookmarks_telemetry.js",
    "Bookmarks-toolbar Glean events: setting changes, bookmarks added to the toolbar, and opening "
    "a bookmark from it.",
    [2084649, 2084650, 2084651],
)
CSEC(
    2525,
    "STRONG",
    "browser/components/places/tests/browser/browser_bookmark_popup.js; browser_bookmarkProperties_cancel.js; "
    "browser_bookmarkProperties_no_user_actions.js; browser_bookmarkProperties_editFolder.js; "
    "browser_bookmarksProperties.js; browser_views_liveupdate.js",
    "Section 400418 - whether an add/edit from the star button, toolbar or Library is committed "
    "immediately or only on confirm - is exactly what browser_bookmark_popup.js and the "
    "bookmarkProperties tests assert (including the no-user-actions and cancel paths).",
    [400418],
)
C(
    2525,
    "STRONG",
    "browser/components/places/tests/browser/browser_addBookmarkForFrame.js; "
    "browser_bookmarkProperties_bookmarkAllTabs.js; browser_bookmark_current_tabs.js",
    "Bookmarking from the Bookmarks menu / hamburger menu and editing it there.",
    [2084489, 2084490],
)
C(
    2525,
    "MEDIUM",
    "browser/components/migration/tests/browser/; browser/components/places/tests/browser/browser_bookmark_backup_export_import.js",
    "Per-browser import (Chrome / Safari / Edge / RTL build), drag-to-File-Explorer, dark-mode "
    "rendering, theme rendering and the scroll-while-menu-open bug have no equivalent in-tree "
    "assertion.",
    [2084639, 2084640, 2084641, 2084642, 2084635, 2084636, 2084633, 2084652, 2084491,
     2084587],
)

# ---------------------------------------------------------------- suite 100482
# "Share Folder / Curated Link Sharing" (86 cases).
# Tree: browser/components/contentsharing/tests/browser/ (6 tests) - a thin suite for a
# large, server-backed feature.
C(
    100482,
    "STRONG",
    "browser/components/contentsharing/tests/browser/browser_testShareBookmarks.js; "
    "browser_testShareBookmarksFromSidebar.js; browser_testShareTabGroup.js; browser_testShareTabs.js; "
    "browser_testShareAuth.js",
    "The 'Share Folder' / 'Share Group' / 'Create Shareable Link' entry points from the bookmarks "
    "menu, the bookmarks sidebar, the tab-group menu and a multi-tab selection, plus the "
    "not-signed-in state of the share panel.",
    [4033941, 4033942, 4033943, 4033945, 4033949, 4033951, 4033953, 4033954,
     4033950, 4033955, 4033957, 4033961],
)
C(
    100482,
    "STRONG",
    "browser/components/contentsharing/tests/browser/browser_testShareFolderEmpties.js",
    "An empty bookmarks folder or empty tab group cannot be shared.",
    [4033970, 4033974],
)
C(
    100482,
    "MEDIUM",
    "browser/components/contentsharing/tests/browser/browser_testShareBookmarks.js; browser_testShareTabGroup.js",
    "Item-count limits, the shared page itself, cross-browser rendering, moderation, error states, "
    "themes/HCM/screen-reader and telemetry are all server-side or visual and are not covered by "
    "the six in-tree tests.",
    [4033944, 4033956, 4033971, 4033972, 4033973, 4033975, 4033976, 4033977, 4033978,
     4033979, 4033980, 4033989, 4033990, 4033988, 4034024],
)