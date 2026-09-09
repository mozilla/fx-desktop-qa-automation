"""Critical round -- Session Restore (suite 68) and the release smoke matrix (suite 71226).

Suite 71226 turns out not to be a session-restore suite at all: it is a broad release
regression matrix that re-walks live sites, themes, printing, PDF, scrolling, crash
reporting and Sync. Its session-restore section duplicates suite 68 verbatim, so the two are
handled together here. 71226's printing section (675812) and PDF section (675817) are
covered in c_03_printing_pdf.py instead.
"""

from _ledger import C

SS = "browser/components/sessionstore/test/"
SSM = SS + "marionette/"
FXV = "browser/components/firefoxview/tests/browser/"

# ---------------------------------------------------------------- restore previous session
C(
    68,
    "STRONG",
    SSM + "test_restore_manually.py; test_restore_windows_after_restart_and_quit.py; "
    "test_restore_windows_after_close_last_tabs.py; session_store_test_case.py",
    "The marionette suite restarts the browser for real and asserts the previous window and "
    "tab set comes back when restore is invoked manually -- the same flow as 'Restore "
    "Previous Session' from the Firefox menu.",
    [114837, 3248823],
)
C(
    68,
    "STRONG",
    "browser/components/privatebrowsing/test/browser/browser_privatebrowsing_noSessionRestoreMenuOption.js",
    "A test dedicated to exactly this assertion: the Restore Previous Session menu item is "
    "absent in a private window.",
    [115426, 3248828],
)
C(
    68,
    "STRONG",
    SSM + "test_new_tab_on_restore.py",
    "Covers about:blank / about:newtab surviving a restore rather than being dropped or "
    "duplicated.",
    [116003],
)
C(
    68,
    "STRONG",
    SS + "browser_undoCloseById.js; browser_undoCloseById_targetWindow.js; "
    "browser_closed_tabs_windows.js; " + FXV + "browser_recentlyclosed_firefoxview.js",
    "Reopening a recently closed tab is covered from the sessionstore API side "
    "(test_ClosedTabMethods, undoCloseById) and from the Firefox View UI side "
    "(test_restore_tab).",
    [463046, 3248830],
)
C(
    68,
    "STRONG",
    "browser/components/preferences/tests/home/browser_startup_browser_restore_session.js",
    "test_startup_browser_restore drives the 'Open previous windows and tabs' startup "
    "preference and asserts the resulting startup behaviour.",
    [114844],
)

# ---------------------------------------------------------------- restore last closed action
C(
    68,
    "STRONG",
    SS
    + "browser_restoreLastClosedTabOrWindowOrSession.js; browser_restoreLastActionCorrectOrder.js; "
    "browser_615394-SSWindowState_events_undoCloseWindow.js",
    "test_undo_last_action, test_reopen_last_tab_if_no_closed_actions and "
    "test_reopen_last_session_if_no_closed_actions cover restoring the last closed window and "
    "the last closed session via the undo-last-action shortcut; browser_restoreLastActionCorrectOrder.js "
    "covers restoring several closed windows in the right order.",
    [2186918, 2186919, 2197846, 3248829],
)
C(
    68,
    "STRONG",
    SS
    + "browser_restoreLastClosedTabOrWindowOrSession.js; browser_forget_closed_tab_window_byId.js",
    "test_user_clears_history asserts that clearing browsing data and history resets the "
    "last-closed-action stack, which is what this case checks.",
    [2191112],
)
C(
    68,
    "STRONG",
    SSM + "test_persist_closed_tabs_restore_manually.py",
    "Closed tabs persisted across a restart and then restored manually -- the restart half of "
    "this case.",
    [2191113],
)
C(
    68,
    "STRONG",
    SS + "browser_restoreLastClosedTabOrWindowOrSession.js; "
    "browser_615394-SSWindowState_events_undoCloseWindow.js; browser_closed_tabs_closed_windows.js",
    "Reopening a closed window through the restore-last-closed path is covered directly.",
    [1569329],
)

# ---------------------------------------------------------------- recently closed across windows
C(
    68,
    "STRONG",
    SS
    + "browser_closed_tabs_windows.js; browser_closed_objects_changed_notifications_tabs.js; "
    "browser_closed_objects_changed_notifications_windows.js; browser_closedId.js",
    "test_ClosedTabMethods builds closed tabs across several windows and asserts the "
    "aggregated closed-tab list each window sees, which is the mechanic behind the history "
    "menu showing other windows' closed tabs.",
    [2333478],
)
C(
    68,
    "STRONG",
    FXV + "browser_recentlyclosed_firefoxview.js",
    "test_list_updates and test_list_ordering assert a tab closed in one window appears in "
    "the Firefox View recently-closed list seen from another.",
    [2333480],
)
C(
    68,
    "STRONG",
    FXV
    + "browser_recentlyclosed_firefoxview.js; "
    + SS
    + "browser_forget_closed_tab_window_byId.js; "
    "browser_forget_async_closings.js",
    "test_dismiss_tab covers dismissing an entry from the recently-closed list, and the forget "
    "tests cover the underlying removal across windows.",
    [2333484],
)

C(
    68,
    "STRONG",
    SS + "browser_formdata.js; browser_formdata_xpath.js; browser_formdata_format.js; "
    "browser_formdata_face.js; browser_formdata_max_size.js",
    "Seven dedicated form-data tests fill inputs of each type, restore, and assert the values "
    "come back -- including the field-identification and size-limit edge cases.",
    [114830],
)

# ---------------------------------------------------------------- quit / close confirmation
C(
    68,
    "STRONG",
    "browser/components/tests/browser/browser_quit_multiple_tabs.js; browser_quit_shortcut_warning.js; "
    "browser_quit_close_current_tab.js; browser_quit_disabled.js",
    "test_check_right_prompt and test_quit_shortcut cover which confirmation prompt is raised "
    "when quitting with multiple tabs open and when quitting via the keyboard shortcut, "
    "including the warn-on-quit and warn-on-close-tabs preference combinations these cases "
    "enumerate.",
    [1569303, 1569307, 1569317, 1569323],
)

# ---------------------------------------------------------------- suite 71226 non-restore rows
C(
    71226,
    "STRONG",
    "browser/components/profiles/tests/browser/browser_create_profile_page_test.js; "
    "browser_delete_profile_page_test.js",
    "Creating a profile from inside Firefox and deleting one with or without its data are "
    "both covered by dedicated profile-page tests.",
    [3248839, 3248840],
)
C(
    71226,
    "STRONG",
    "browser/components/privatebrowsing/test/browser/browser_privatebrowsing_ui.js; "
    "browser_privatebrowsing_about.js",
    "Opening a private window and the resulting private-window UI state is covered; the "
    "keyboard shortcut is the standard command path these tests invoke.",
    [3248836],
)
C(
    71226,
    "STRONG",
    "browser/components/downloads/test/browser/browser_indicatorDrop.js; browser_libraryDrop.js",
    "Starting a download by dropping a link on the downloads indicator or the Library is "
    "covered by both drop tests.",
    [3248859],
)

# ---------------------------------------------------------------- reviewed but kept
C(
    68,
    "MEDIUM",
    SSM + "test_restore_manually.py",
    "The dirty-profile, post-update (clean and dirty profile) and crashed-twice variants. The "
    "tree restores from a clean automated profile; the manual value here is the profile state "
    "and the update/crash transition, none of which the marionette harness reproduces.",
    [3945, 114838, 114843, 114841, 3248824, 3248825, 3248826, 3248827],
)
C(
    68,
    "MEDIUM",
    "browser/components/privatebrowsing/test/browser/browser_privatebrowsing_aboutSessionRestore.js",
    "about:sessionrestore behaviour in a private window is covered, but restoring a session "
    "from the about:support entry point is not.",
    [462654],
)
C(
    68,
    "MEDIUM",
    SS
    + "browser_pinned_tabs.js; browser_closed_tabs_windows.js; "
    + FXV
    + "browser_recentlyclosed_firefoxview.js",
    "The recently-closed variants that depend on history preferences (Custom settings, Never "
    "remember), on private windows being excluded, on automatic session restore being on, and "
    "on closed pinned tabs from several windows. The tree covers the default configuration "
    "only.",
    [2333481, 2333483, 2333485, 2333486, 2333487, 2198152, 2198153, 2198377],
)
C(
    68,
    "MEDIUM",
    SS + "browser_restored_window_features.js",
    "Window geometry on restore is partially covered, but not the minimized-window exclusion, "
    "and no test walks the full 'all options are remembered' checklist.",
    [171451, 462981],
)
C(
    68,
    "MEDIUM",
    "browser/components/preferences/tests/home/browser_startup_browser_restore_session.js",
    "The always-restore preference is covered; the restore-once variant is not.",
    [115423],
)
C(
    68,
    "MEDIUM",
    "browser/components/downloads/test/browser/browser_downloads_pauseResume.js",
    "Pause/resume of a live download is covered, but nothing restarts the browser mid-download "
    "and asserts the transfer resumes after session restore.",
    [114831],
)
C(
    68,
    "MEDIUM",
    "browser/components/tests/browser/browser_quit_multiple_tabs.js",
    "Quitting from the OS toolbar / dock and the private-window no-warning case depend on "
    "window-manager interaction the browser-chrome harness does not drive.",
    [1569299, 1569311, 1569316],
)
C(
    71226,
    "MEDIUM",
    "n/a",
    "Section 675805 walks ten live third-party sites (openai.com, mail.google.com, facebook.com, "
    "x.com, reddit.com, amazon.com, youtube.com, netflix.com, spotify.com, mayoclinic.com). "
    "Third-party web compat against the live web is out of scope for in-tree automation.",
    [
        3248841,
        3248842,
        3248843,
        3248844,
        3248845,
        3248846,
        3248847,
        3248848,
        3248849,
        3248850,
    ],
)
C(
    71226,
    "MEDIUM",
    "browser/base/content/test/performance/browser_windowclose.js",
    "Toolbar customisation persistence, the built-in themes, high-contrast interaction and RTL "
    "layout are visual/appearance checks the tree does not assert at this altitude.",
    [3248869, 3248870, 3248871, 3248873, 3248874],
)
C(
    71226,
    "MEDIUM",
    "n/a",
    "Crash-reporter rows: unsubmitted reports, submission to Socorro, local report storage and "
    "localisation of the crash dialog. These need a real crash plus a live Socorro endpoint.",
    [3248831, 3248832, 3248833, 3248834],
)
C(
    71226,
    "MEDIUM",
    "gfx/layers/apz/test/mochitest/",
    "APZ has extensive scroll tests, but they are synthetic-content unit tests; these rows are "
    "subjective smoothness checks on image-heavy, video and PDF pages.",
    [3248865, 3248866, 3248867],
)
C(
    71226,
    "MEDIUM",
    "services/sync/tests/",
    "Sync between two profiles, Send Tab to Device and signing in with an existing account all "
    "need live FxA credentials and a second device.",
    [3248885, 3248886, 3248887],
)
C(
    71226,
    "MEDIUM",
    "n/a",
    "Copy/paste of images via file-hosting sites and of tables out of other browsers -- both "
    "depend on third-party applications and live services.",
    [3248855, 3248857],
)
