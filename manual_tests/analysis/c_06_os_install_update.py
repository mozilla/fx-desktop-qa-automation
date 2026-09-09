"""Critical round -- OS integration, installers, updates and profile migration.

Suites: 74 (Migration from other browsers), 1940 (OS integration), 5252 (Installers),
2052 (Uninstall / Refresh), 5260 (Background Update Agent), 24370 (Third-party interop).

The split here is sharp. Profile migration is one of the best-covered features in the whole
comparison: browser/components/migration/tests has a per-source xpcshell test for every data
type (Chrome, Chromium, Edge, Safari, 360se) plus browser-chrome tests for the wizard, the
entry points and the file importers. Taskbar Tabs likewise has 13 dedicated tests.

Everything that runs *outside* the browser -- stub and full installers, UAC prompts, MSIX
packaging, code signing, .dmg and .pkg, the uninstaller, Windows taskbar and Start menu
pinning, antivirus interop -- has no in-tree equivalent and stays manual.
"""

from _ledger import C
from c_util import CREST

MIG = "browser/components/migration/tests/"
MIGB = MIG + "browser/"
MIGU = MIG + "unit/"
TT = "browser/components/taskbartabs/test/browser/"
BGU = "toolkit/mozapps/update/tests/"
SEARCHT = "browser/components/search/test/browser/telemetry/"

# ================================================================ suite 74: migration
C(
    74,
    "STRONG",
    MIGB
    + "browser_do_migration.js; "
    + MIGU
    + "test_Chrome_bookmarks.js; test_Chrome_history.js; "
    "test_Chrome_passwords.js; test_Chrome_formdata.js; test_Chrome_credit_cards.js; "
    "test_Chrome_permissions.js; test_ChromeMigrationUtils.js",
    "test_successful_migrations drives the wizard with each resource type selected and asserts "
    "what landed; the per-resource xpcshell tests read real Chrome profile fixtures for "
    "bookmarks, history, passwords, form data, cards and permissions. Together this is 'all "
    "data, or data separately, from Chrome'.",
    [2139251],
)
C(
    74,
    "STRONG",
    MIGU
    + "test_Edge_db_migration.js; test_Edge_registry_migration.js; "
    + MIGB
    + "browser_edge_bookmarks_success_strings.js; browser_do_migration.js",
    "Edge migration is covered from both storage backends it uses (the ESE database and the "
    "registry), with the success-string assertions on top.",
    [2140092],
)
C(
    74,
    "STRONG",
    MIGU
    + "test_Safari_bookmarks.js; test_Safari_history.js; test_Safari_permissions.js; "
    + MIGB
    + "browser_safari_passwords.js; browser_safari_permissions.js",
    "Safari has dedicated tests per data type, including the permission-prompt path macOS "
    "requires before the source data can be read.",
    [2140104, 2192673, 2195603],
)
C(
    74,
    "STRONG",
    MIGU + "test_Safari_history.js; test_Safari_history_strange_entries.js",
    "Safari history import, including the malformed-entry cases.",
    [2168108],
)
C(
    74,
    "STRONG",
    MIGU + "test_BookmarksFileMigrator.js; " + MIGB + "browser_file_migration.js",
    "test_file_migration and the BookmarksFileMigrator unit test cover importing bookmarks from "
    "an exported HTML file, and test_file_migration_error the malformed-file path. The source "
    "browser that produced the file does not change the code path.",
    [2168109, 2168337],
)
C(
    74,
    "STRONG",
    MIGU + "test_PasswordFileMigrator.js; " + MIGB + "browser_file_migration.js; "
    "browser_chrome_windows_passwords.js",
    "The password file migrator is tested against delimited files, which is the same importer "
    "the CSV and TSV rows exercise.",
    [2192664, 2195600],
)
C(
    74,
    "STRONG",
    MIGB + "browser_extension_migration.js",
    "test_extension_migration_no_matched_extensions asserts the no-matches empty state and "
    "test_extension_migration_fully_matched_extensions the full-success state.",
    [2191232, 2243442],
)
C(
    74,
    "STRONG",
    MIGU + "test_Chrome_credit_cards.js; " + MIGB + "browser_do_migration.js",
    "Chrome payment-method import is covered by a dedicated xpcshell test against a real card "
    "fixture.",
    [2210871],
)
C(
    74,
    "STRONG",
    MIGU
    + "test_MigrationUtils_timedRetry.js; "
    + MIGB
    + "browser_entrypoint_telemetry.js; "
    "browser_dialog_open.js; browser_do_migration.js",
    "testgetRowsFromDBWithoutLocksRetries reads a source database that is locked by the running "
    "source browser and asserts the retry succeeds -- the 'source browser running' half of this "
    "matrix. browser_entrypoint_telemetry.js covers launching the wizard from "
    "MIGRATION_ENTRYPOINTS.PREFERENCES and .BOOKMARKS, i.e. about:preferences and the Library.",
    [27382, 27383, 27385, 27386, 27387, 27388, 29031, 29033, 29087, 27393],
)
C(
    74,
    "STRONG",
    MIGU
    + "test_ChromeMigrationUtils_path.js; test_ChromeMigrationUtils_path_chromium_snap.js; "
    + MIGB
    + "browser_do_migration.js",
    "Chromium on Linux, including the snap-packaged profile location, has its own path-resolution "
    "tests feeding the same migration code.",
    [27389, 27390, 27391],
)

# ================================================================ suite 1940: taskbar tabs
C(
    1940,
    "STRONG",
    TT + "browser_taskbarTabs_pin.js; browser_taskbarTabs_windowManager.js; "
    "browser_taskbarTabs_cmd.js; browser_taskbarTabs_manifest.js; browser_taskbarTabs_icons.js",
    "test_findOrCreateTaskbarTabEnsurePin and test_moveTabIntoTaskbarTabParentWindow cover "
    "opening the Taskbar Tabs window and pinning the site; testTaskbarTabCount and "
    "test_taskbarTab_persistence cover the window bookkeeping.",
    [3814258],
)
C(
    1940,
    "STRONG",
    TT + "browser_taskbarTabs_windowManager.js; browser_taskbarTabs_windowTracker.js; "
    "browser_taskbarTabs_pin.js",
    "test_eject_window_selected_tab, test_count_for_id and test_findOrCreateTaskbarTabParentWindow "
    "cover what happens to the main window when its last tab moves into a Taskbar Tabs window, "
    "and the reverse -- creating a main window when none is open.",
    [3814260, 3814262, 3814264],
)
C(
    1940,
    "STRONG",
    TT + "browser_taskbarTabs_uriTest.js; browser_taskbarTabs_content.js; "
    "browser_taskbarTabs_pageAction.js",
    "browser_taskbarTabs_uriTest.js is dedicated to which navigations stay inside the web-app "
    "window and which are handed back to a normal window, covering both the in-scope navigation "
    "case and opening links in a new tab / window / private window.",
    [3814261, 3814263],
)
C(
    1940,
    "STRONG",
    TT + "browser_taskbarTabs_chromeTest.js; browser_taskbarTabs_nimbus.js; "
    "browser_taskbarTabs_pageAction.js",
    "browser_taskbarTabs_chromeTest.js asserts which chrome the Taskbar Tabs window inherits, "
    "including theming, and browser_taskbarTabs_pageAction.js which windows offer the add-to-"
    "taskbar action.",
    [3814265, 3895126],
)

# ================================================================ suite 1940: default browser
C(
    1940,
    "STRONG",
    "browser/components/shell/test/browser_setDefaultBrowser.js; "
    "browser_windowsSetDefaultAppCmdHandler.js; browser_setDefaultProtocolHandler.js; "
    "browser/components/tests/browser/browser_default_browser_prompt.js; "
    "browser/components/preferences/tests/browser_DefaultBrowserHelper.js; "
    "browser_defaultbrowser_alwayscheck.js",
    "Setting Firefox as the default browser, and the prompt that offers to do so, are covered "
    "from the shell service through to the preferences UI.",
    [2115776],
)
C(
    1940,
    "STRONG",
    "browser/components/tests/browser/browser_default_browser_prompt.js; "
    "toolkit/components/messaging-system/schemas/SpecialMessageActionSchemas/test/browser/browser_sma_default_browser.js; "
    "browser/components/shell/test/browser_setDefaultBrowser.js",
    "The default-browser prompt tests cover the notification being shown, the decline path "
    "leaving the setting untouched, and dismissal without choosing -- the three outcomes these "
    "'Stay with Firefox?' rows enumerate.",
    [2115269, 2115777, 2127833],
)

# ================================================================ suite 1940: withads telemetry
C(
    1940,
    "STRONG",
    SEARCHT
    + "browser_search_telemetry_sources.js; browser_search_telemetry_sources_navigation.js; "
    "browser_search_telemetry_sources_ads.js; browser_search_telemetry_sources_in_content.js",
    "browser_search_telemetry_sources.js asserts the withads probe for the urlbar and searchbar "
    "sources, browser_search_telemetry_sources_navigation.js for the reload and tabhistory "
    "sources, and the ads / in-content tests for the unknown source.",
    [2630932, 2630933, 2630936, 2630937, 2630938],
)

# ================================================================ suite 1940: backup entry points
C(
    1940,
    "STRONG",
    "browser/components/backup/tests/marionette/test_backup.py; "
    "browser/components/backup/tests/browser/browser_settings_restore_from_backup.js; "
    "browser/components/backup/tests/marionette/test_backup_selectable_to_selectable.py; "
    "browser/components/aboutwelcome/tests/browser/browser_aboutwelcome_restore_backup.js",
    "These four rows restate the backup+restore flows already covered in detail for suites "
    "69142 / 73807 / 97961: from about:preferences, from onboarding, with encryption, and with "
    "selectable profiles.",
    [3409353, 3409356, 3409363, 3969303],
)

# ================================================================ suite 1940: WebRTC sharing
C(
    1940,
    "STRONG",
    "browser/base/content/test/webrtc/browser_devices_get_user_media_screen.js; "
    "browser_webrtc_hooks.js; browser_devices_get_user_media_multi_process.js; "
    "browser_indicator_popuphiding.js",
    "The screen/window sharing selection, the sharing indicator, and stopping a share from the "
    "urlbar or the indicator are all driven by the webrtc browser-chrome tests.",
    [2047845, 2047847, 2047848, 2047849],
)

# ================================================================ suite 5260: background updates
C(
    5260,
    "STRONG",
    BGU + "unit_update_binary/marAppInUseBackgroundTaskFailure_win.js; "
    "unit_update_binary/marSuccessPartialWhileBackgroundTaskRunning.js; "
    "unit_background_update/test_backgroundupdate_actions.js; "
    "unit_aus_update/backgroundUpdateTaskInternalUpdater.js",
    "marAppInUseBackgroundTaskFailure_win.js asserts the background task declines to apply an "
    "update while the application is in use, and the partial-update-while-task-running tests "
    "cover the reverse ordering. test_backgroundupdate_actions.js covers the task running to "
    "completion when nothing blocks it.",
    [1811788, 1811789, 1811790],
)
C(
    5260,
    "STRONG",
    BGU + "unit_aus_update/disableBackgroundUpdatesBackgroundTask.js; "
    "unit_aus_update/disableBackgroundUpdatesNonBackgroundTask.js; "
    "browser/browser_aboutPrefs_backgroundUpdateSetting.js; "
    "browser/manual_app_update_only/browser_noBackgroundUpdate.js",
    "The BackgroundAppUpdate policy / pref being disabled and the task consequently not being "
    "scheduled is covered from both the task side and the about:preferences side.",
    [1811792],
)

# ================================================================ reviewed but kept
CREST(
    74,
    "MEDIUM",
    MIGU
    + "test_Chrome_bookmarks.js; test_Safari_bookmarks.js; "
    + MIGB
    + "browser_extension_migration.js",
    "Left over: favicons arriving with imported bookmarks (the tests assert the bookmark rows, "
    "not the icons), the payment-methods option being hidden when the source has none, the "
    "partial-success extension state, extensions finishing installation after a restart, and "
    "the Windows 10 'import wizard does not freeze while Edge is running' regression.",
)
CREST(
    1940,
    "MEDIUM",
    "browser/components/shell/test/browser_setDefaultBrowser.js",
    "The remainder is Windows and macOS shell integration that lives outside the browser "
    "process: taskbar and Start menu pinning surviving updates and reboots, pinning websites "
    "from the Start menu, the Dock and Finder on macOS, the stub-installer launcher, the "
    "set-as-default guidance notifications that render as OS toasts, and opening links from an "
    "external mail client. None of it is reachable from the browser-chrome or marionette "
    "harnesses.",
)
CREST(
    5252,
    "MEDIUM",
    "n/a",
    "All 47 rows run before or around the browser rather than inside it: stub and full installer "
    "UI, UAC elevation as admin and non-admin, cancel/resume, pave-over and re-install prompts, "
    "non-ASCII and unwritable install directories, .msi and MSIX packaging, macOS .dmg / .pkg "
    "install and code signing, Ubuntu packages, and taskbar pinning performed by the installer. "
    "The tree ships packaging manifests but no installer test harness.",
)
CREST(
    2052,
    "MEDIUM",
    "browser/components/uitour/test/browser_UITour_resetProfile.js",
    "browser_UITour_resetProfile.js only asserts that UITour can request a profile reset. The "
    "Refresh Firefox entry points these rows use -- the uninstall helper, Add/Remove Programs, "
    "the running-Firefox case -- and the Windows uninstaller and its survey redirect are all "
    "outside the browser.",
)
CREST(
    5260,
    "MEDIUM",
    BGU + "unit_background_update/test_backgroundupdate_reason.js",
    "The scheduler being torn down when the install becomes ineligible (language pack, "
    "uninstall) and the unzipped / unelevated / MSIX build variants all depend on a real "
    "Windows Task Scheduler registration.",
)
CREST(
    24370,
    "MEDIUM",
    "n/a",
    "Third-party antivirus and OS interop: Firefox behaviour after an AV update, with AV options "
    "on and off, AV add-ons not self-enabling, the default search engine surviving an AV "
    "install, enterprise root certificates versus TLS client auth, CDM modules, Snap layouts and "
    "background build updates. Each needs real third-party software installed on the host.",
)
