from _ledger import C

# ---------------------------------------------------------------- suite 2103
# "Tabbed Browser" (113 cases). Tree: browser/components/tabbrowser/test/browser/
# = 193 tabs/ + 6 dragdrop/ + 6 smarttabgrouping/ + 13 tabMediaIndicator/ tests.
C(
    2103,
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_new_tab_url.js; browser_new_tab_insert_position.js; "
    "browser_addAdjacentNewTab.js; browser_addTab_index.js; browser_tabkeynavigation.js; "
    "browser_middle_click_new_tab_button_loads_clipboard.js",
    "Opening a new tab from the '+' button, keyboard and middle-click on the tab bar, "
    "including insertion position.",
    [134442, 134453, 134454],
)
C(
    2103,
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_contextmenu_openlink_after_tabnavigated.js; "
    "browser_window_open_modifiers.js; browser_openURI_background.js; browser_tabs_openURI_after_current.js; "
    "browser_relatedTabs.js",
    "Opening links in new foreground / background tabs by modifier-click, middle-click and "
    "context menu, and where the new tab lands.",
    [134444, 134455, 134456],
)
C(
    2103,
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_tabDrop.js",
    "Dropping a link/text onto the tab strip opens it in a new tab.",
    [134458],
)
C(
    2103,
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_tab_dragdrop.js; browser_tab_dragdrop2.js; "
    "browser_tab_drag_drop_perwindow.js; browser_tabReorder.js; browser_tabReorder_overflow.js; "
    "browser_tabReorder_vertical.js; browser_tab_detach_restore.js",
    "Tab drag-and-drop: reorder in-strip, overflowed strip, vertical strip, detach to a new "
    "window and drag between windows.",
    [135373, 175217],
)
C(
    2103,
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_multiselect_tabs_reorder.js; "
    "browser_multiselect_tabs_move.js; browser_multiselect_tabs_move_to_new_window_contextmenu.js; "
    "browser_multiselect_tabs_move_to_another_window_drag.js",
    "Reordering and moving a multi-selection of tabs.",
    [3139924, 246989],
)
C(
    2103,
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_pinnedTabs.js; browser_pinnedTabs_clickOpen.js; "
    "browser_pinnedTabs_closeByKeyboard.js; browser_standalonePinnedTab.js; browser_pinned_and_hidden_tabs.js; "
    "browser/components/tabbrowser/test/browser/dragdrop/browser_drag_to_pin.js",
    "Pin/unpin, pinned-tab ordering, and a link clicked in a pinned tab opening after the "
    "pinned block.",
    [134722, 134723, 171447],
)
C(
    2103,
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_multiselect_tabs_close.js; "
    "browser_multiselect_tabs_close_other_tabs.js; browser_multiselect_tabs_close_tabs_to_the_right.js; "
    "browser_multiselect_tabs_close_tabs_to_the_left.js; browser_multiselect_tabs_close_using_shortcuts.js; "
    "browser_removeAllTabsBut.js; browser_removeTabsToTheEnd.js; browser_removeTabsToTheStart.js",
    "The full close-tabs matrix: single, multi-selection, close-others, close-to-the-right/left, "
    "and the keyboard shortcuts.",
    [134647, 134649, 246980, 246986, 246983, 246990],
)
C(
    2103,
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_undo_close_tabs.js; "
    "browser_undo_close_tabs_at_start.js; browser/components/customizableui/test/browser_history_recently_closed.js",
    "Reopen closed tab by keyboard, by tab context menu, and the History-menu list.",
    [134640, 134648, 134650],
)
C(
    2103,
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_ctrlTab.js; browser_selectTabAtIndex.js; "
    "browser_tabswitch_select.js; browser_tabfocus.js; browser_tabkeynavigation.js; browser_tab_move_active_tab.js; "
    "browser_positional_attributes.js",
    "Tab switching by Ctrl+Tab / Ctrl+1..9 / arrow keys, moving the active tab by keyboard, "
    "and the selected-tab attribute.",
    [134634, 134654, 134465, 134646, 178022],
)
C(
    2103,
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabMediaIndicator/browser_mute.js; browser_mute2.js; "
    "browser_mute_persist_navigation.js; browser_mute_webAudio.js; browser_mediaPlayback_mute.js; "
    "browser/components/tabbrowser/test/browser/tabs/browser_audioTabIcon.js; "
    "browser_multiselect_tabs_mute_unmute.js; browser_multiselect_tabs_play.js",
    "Mute/unmute a tab from the sound icon and from the context menu, single and multi-select, "
    "plus persistence across navigation.",
    [134719, 246981, 246982, 246984],
)
C(
    2103,
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_multiselect_tabs_pin_unpin.js; "
    "browser_multiselect_tabs_bookmark.js; browser_multiselect_tabs_drag_to_bookmarks_toolbar.js; "
    "browser_multiselect_tabs_duplicate.js; browser_multiselect_tabs_reload.js; "
    "browser_multiselect_tabs_using_Shift.js; browser_multiselect_tabs_using_Ctrl.js; "
    "browser_multiselect_tabs_using_Shift_and_Ctrl.js; browser_multiselect_tabs_using_keyboard.js",
    "Multi-select construction (Ctrl / Shift / keyboard) and every bulk action the manual suite "
    "lists: pin, bookmark (menu + drag), duplicate, reload.",
    [246978, 246979, 246988, 4038574, 134464],
)
C(
    2103,
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_tabContextMenu_altStructure.js; "
    "browser_tabContextMenu_keyboard.js; browser_visibleTabs_contextMenu.js; browser_hiddentab_contextmenu.js",
    "Tab context-menu structure and item behaviour, mouse and keyboard driven.",
    [246991],
)
C(
    2103,
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_tab_preview.js; browser_visibleTabs_tabPreview.js; "
    "browser_tab_tooltips.js",
    "Tab hover preview card, including with a large/overflowing tab strip.",
    [2693897],
)
C(
    2103,
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_tab_groups.js; browser_tab_group_menu.js; "
    "browser_tab_groups_tabContextMenu.js; browser_tab_groups_list.js; browser_tab_groups_insertAfterCurrent.js; "
    "browser_tab_groups_keyboard_focus.js; browser_tab_groups_a11y.js",
    "Tab-group CRUD from the tab context menu and the group menu: create, rename/recolour, "
    "add tab, remove tab, ungroup, list.",
    [2793046, 2793048, 2793051, 2793052, 2796550],
)
C(
    2103,
    "STRONG",
    "browser/components/sessionstore/test/browser_tab_groups_save_on_window_close.js; browser_tab_groups_saved.js; "
    "browser_tab_groups_restore_saved.js; browser_tab_groups_restore_to_group.js; browser_tab_groups_restore_simple.js; "
    "browser_tab_groups_restore_multiple.js; browser_tab_groups_restore_closed_in_open_window.js; "
    "browser_tab_groups_closed.js; browser_tab_groups_undo.js; browser_tab_groups_state.js",
    "Save-and-close a group, restore closed tabs back into their group, and group restore from a "
    "previous session - 10 dedicated sessionstore tests.",
    [2793050, 2804875, 2806183],
)
C(
    2103,
    "STRONG",
    "browser/components/tabbrowser/test/browser/smarttabgrouping/browser_tab_grouping.js; "
    "browser_tab_grouping_search.js; browser_tab_grouping_suggestions_checkbox.js; browser_tab_grouping_telemetry.js",
    "'Suggest more tabs' on the create/manage tab-group panel and adding suggested tabs.",
    [2946450, 2947536, 2946545, 2960359],
)
# --- Split View (section 864078)
C(
    2103,
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_tab_splitview.js; browser_tab_splitview_contextmenu.js; "
    "browser_tab_splitview_alt_click.js; browser_tab_splitview_tab_order.js",
    "Creating and separating a split view from the tab context menu (one or two tabs selected, "
    "horizontal and vertical strips), from a link, and dissolving it by closing one side.",
    [3903433, 3903434, 3903435, 3903441, 3903440, 3903453, 3903454],
)
C(
    2103,
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_tab_splitview_resize.js; "
    "browser_tab_splitview_splitter_keyboard.js; browser_tab_splitview_splitter_keyboard_boundary.js",
    "Resizing the split via the splitter, with the mouse and with keyboard arrows (incl. boundaries).",
    [3903443, 3903444],
)
C(
    2103,
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_tab_splitview_footer.js; "
    "browser_tab_splitview_about_opentabs.js; browser_tab_splitview_keyboard_focus.js",
    "The three-dot footer menu inside a split view and the dedicated new-tab page shown when "
    "adding a split view.",
    [3903446, 3903449],
)
C(
    2103,
    "STRONG",
    "browser/components/tabbrowser/test/browser/dragdrop/browser_drag_splitview.js; "
    "browser_drag_multiselected_splitview.js; browser_drop_link_splitview_unselected.js",
    "Dragging a split view within the strip and dropping links into it.",
    [3903436],
)
C(
    2103,
    "STRONG",
    "browser/components/sessionstore/test/browser_splitview_restore_in_closed_window.js; "
    "browser_splitview_integer_ids.js; browser_splitview_string_migration.js; "
    "browser/components/tabbrowser/test/browser/tabs/browser_replacewithwindow_splitview.js",
    "Split views survive session restore and window replacement.",
    [3903451],
)
C(
    2103,
    "MEDIUM",
    "browser/components/tabbrowser/test/browser/tabs/browser_tab_manager_drag.js; browser_tab_manager_groups.js; "
    "browser_tab_manager_close.js; browser_list_all_tabs_menu_items.js; browser_overflowScroll.js; "
    "browser_tab_label_during_reload.js; browser_selectMRUOnClose.js; browser_close_tab_by_dblclick.js",
    "Adjacent behaviour is automated but not the specific manual assertion (List-all-tabs drag of a "
    "split view, overflow-button pulse, middle-click close, reload-overriding-cache, Esc-to-stop, "
    "pinned-tab refresh after restart/crash, hover-preview content types and DPI).",
    [143585, 178018, 134645, 134641, 134642, 134643, 134720, 134724, 134726,
     2693898, 2693900, 3903437, 3903438, 3903439, 3903442, 3903445, 3903447,
     3903448, 3903450, 3903452, 2798221, 2793047, 2804878, 2804879, 246985,
     134443, 134445, 134457, 134459, 134460, 134461, 134462, 134463, 3122128],
)

# ---------------------------------------------------------------- suite 53810
# "Sidebar" (105 cases). Tree: browser/components/sidebar/tests/browser/ = 55 tests.
C(
    53810,
    "STRONG",
    "browser/components/sidebar/tests/browser/browser_toolbar_sidebar_button.js; browser_view_sidebar_menu.js; "
    "browser_sidebar_menubar_item_commands.js; browser_sidebar_macmenu.js",
    "Enabling/showing the sidebar from the toolbar button, the View menu and the menu bar, "
    "including the fresh-profile default placement.",
    [2639190, 2639191],
)
C(
    53810,
    "STRONG",
    "browser/components/sidebar/tests/browser/browser_resize_sidebar.js; browser_sidebar_max_width.js; "
    "browser_launcher_splitter_visibility.js; browser_sidebar_splitter_keyboard.js",
    "Resizing the launcher and the panel by dragging the splitter (and by keyboard), and the "
    "75%-of-window maximum width.",
    [2639208, 2652538, 2652542],
)
C(
    53810,
    "STRONG",
    "browser/components/sidebar/tests/browser/browser_sidebar_position.js; legacy/browser_sidebar_move.js",
    "Moving the sidebar to the right-hand side.",
    [2639212],
)
C(
    53810,
    "STRONG",
    "browser/components/sidebar/tests/browser/browser_customize_sidebar.js; browser_vertical_tabs.js; "
    "browser_vertical_tabs_cui_reset.js; browser_verticalTabs_widget_placements.js",
    "Customize Sidebar: switching between vertical and horizontal tabs and the expand/collapse "
    "settings, plus the resulting widget placements.",
    [2668317, 2639225, 2652980],
)
C(
    53810,
    "STRONG",
    "browser/components/sidebar/tests/browser/browser_sidebar_prefs.js; legacy/browser_sidebar_persist.js; "
    "browser_adopt_sidebar_from_opener.js; browser_tools_migration.js",
    "Sidebar state and every Customize-Sidebar setting (tools, position, vertical/horizontal, "
    "hide-horizontal-tabs) persisting across new windows and restarts.",
    [2639224, 2655240, 2655241, 2655242, 2659961, 2659962],
)
C(
    53810,
    "STRONG",
    "browser/components/sidebar/tests/browser/browser_hide_sidebar.js; browser_hide_sidebar_on_popup.js; "
    "browser_launcher_hidden_restore.js",
    "'Hide sidebar' and restoring the hidden launcher.",
    [2651719],
)
C(
    53810,
    "STRONG",
    "browser/components/sidebar/tests/browser/browser_sidebar_panel_states.js; browser_sidebar_panel_header.js; "
    "browser_sidebar_escape_collapse.js; browser_tools_overflow.js",
    "Clicking a tool opens its panel (collapsed or expanded launcher), clicking it again or the "
    "X closes it, and clicking a different tool switches the panel.",
    [2651960, 2651961, 2652108, 2652109],
)
C(
    53810,
    "STRONG",
    "browser/components/sidebar/tests/browser/browser_history_sidebar.js; browser_history_keyboard_navigation.js; "
    "browser_history_multiselect.js; browser_delete_sidebar_history.js; browser_syncedtabs_sidebar.js; "
    "browser_bookmarks_sidebar.js; browser_opentabs_sidebar.js",
    "The History, Synced Tabs, Bookmarks and Open Tabs panels themselves - entry points and contents.",
    [2651959],
)
C(
    53810,
    "STRONG",
    "browser/components/sidebar/tests/browser/browser_extensions_sidebar.js",
    "Managing pinned extensions in the sidebar and their icons disappearing when disabled.",
    [2652535, 2652537],
)
C(
    53810,
    "STRONG",
    "browser/components/sidebar/tests/browser/browser_sidebar_expand_on_hover.js; browser_customize_sidebar.js",
    "Enabling 'Expand on hover' in Customize Sidebar and the launcher expanding/collapsing on hover.",
    [2946562, 2947561],
)
# --- vertical tabs actions (section 518352) - these are tabbrowser behaviours surfaced in the sidebar
C(
    53810,
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_tabReorder_vertical.js; "
    "browser/components/tabbrowser/test/browser/dragdrop/browser_drag_to_pin.js; "
    "browser/components/sidebar/tests/browser/browser_vertical_tabs.js; browser_vertical_tabs_stacking_context.js",
    "Reordering vertical tabs by drag-and-drop and dragging a tab into the pinned section.",
    [2652718, 2652720, 2652387],
)
C(
    53810,
    "STRONG",
    "browser/components/tabbrowser/test/browser/tabs/browser_multiselect_tabs_duplicate.js; "
    "browser_multiselect_tabs_reload.js; browser_multiselect_tabs_bookmark.js; browser_multiselect_tabs_close.js; "
    "browser_multiselect_tabs_move.js; browser_undo_close_tabs.js; "
    "browser/components/tabbrowser/test/browser/tabMediaIndicator/browser_mute.js; "
    "browser/components/sidebar/tests/browser/browser_sidebar_collapsed_close_tab_button.js; "
    "browser_sidebar_context_menu.js",
    "The vertical-tab context-menu actions (move, duplicate, mute/unmute, reload, bookmark, close, "
    "close multiple, reopen closed) are the same tabbrowser commands, all covered.",
    [2652111, 2652112, 2652383, 2652384, 2652386, 2652388, 2652392, 2652393],
)
C(
    53810,
    "MEDIUM",
    "browser/components/sidebar/tests/browser/browser_sidebar_expand_on_hover.js; browser_a11y_sidebar.js; "
    "browser_glean_sidebar.js; browser_sidebar_nimbus.js; browser_sidebar_pinned_tab_promo.js; "
    "browser_domfullscreen_sidebar.js; browser_f11_fullscreen_sidebar.js",
    "One in-tree test carries the whole expand-on-hover feature; the manual suite's 40 cases for it "
    "(HCM, HiDPI, themes, screen readers, animations, window sizes, crash persistence, audio "
    "indicators, tab groups, previews, notifications) go far beyond it. Same for the visual/a11y "
    "cases in the main section.",
    [2639226, 2639213, 2651957, 2651958, 2652531, 2652533, 2652534, 2652539,
     2652541, 2652543, 2652545, 2652547, 2652385, 2652391, 2652395, 2652396,
     2652719, 2652727, 2652733,
     2947562, 2947563, 2947565, 2947567, 2947482, 2947648, 2947649, 2947650,
     2947651, 2947652, 2946553, 2947502, 2947503, 2947504, 2947505, 2947530,
     2947539, 2947540, 2947557, 2947808, 2947809, 2947811, 2947816, 2948253,
     2948255, 2948304, 2955183, 2955184],
)