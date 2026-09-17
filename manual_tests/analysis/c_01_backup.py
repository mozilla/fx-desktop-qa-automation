"""Critical round -- Backup and Restore (suites 69142 / 73807 / 97961).

Those three suites are near-identical copies of the same backup+restore matrix (162
critical, not-yet-automated cases between them), so each cluster below carries the case ids
from all three.

The load-bearing in-tree test is the marionette pair
browser/components/backup/tests/marionette/test_backup.py + backup_test_base.py: it creates a
real backup, recovers it into a fresh profile, and then asserts resource by resource that
cookies, logins, certificates, addresses, payment methods, form history, bookmarks, history,
preferences, permissions, sessionstore and the newtab wallpaper all survived. That one test
subsumes most of the "verify <data category> is properly restored" rows.
"""

from _ledger import C

BASE = "browser/components/backup/tests/"
MAR = BASE + "marionette/"
BROWSER = BASE + "browser/"
XPC = BASE + "xpcshell/"

# ---------------------------------------------------------------- restored data matrix
C(
    69142,
    "STRONG",
    MAR + "test_backup.py; backup_test_base.py",
    "Full create-backup -> recover-into-new-profile cycle, then verify_recovered_bookmarks() "
    "and verify_recovered_history() assert the bookmark toolbar contents, nested Library "
    "folders and the whole history set survive the round trip.",
    [3163608, 3336016, 3971135, 3163612, 3336020, 3971139, 3163614, 3336022, 3971141],
)
C(
    69142,
    "STRONG",
    MAR + "test_backup.py; " + XPC + "test_CredentialsAndSecurityBackupResource.js",
    "verify_recovered_test_login() and verify_recovered_test_certificate() assert saved "
    "logins and an imported certificate are present after recovery.",
    [3163633, 3336055, 3971186, 3163629, 3336033, 3971153],
)
C(
    69142,
    "STRONG",
    MAR + "test_backup.py; " + XPC + "test_FormHistoryBackupResource.js",
    "verify_recovered_saved_address() and verify_recovered_payment_methods() assert restored "
    "autofill addresses and credit cards match, decrypting the card number through the "
    "OSKeyStore.",
    [3163659, 3336071, 3971207, 3163660, 3336073, 3971209],
)
C(
    69142,
    "STRONG",
    MAR + "test_backup.py; " + XPC + "test_SessionStoreBackupResource.js; "
    "test_SessionStoreBackupResource_mockSessionStore.js",
    "verify_recovered_sessionstore() asserts the window/tab set recorded before the backup is "
    "the one restored afterwards.",
    [3163648, 3336060, 3971196],
)
C(
    69142,
    "STRONG",
    XPC
    + "test_PreferencesBackupResource_searchEngines.js; test_PreferencesBackupResource.js; "
    + MAR
    + "test_backup.py",
    "A dedicated resource test for the search-engine payload plus verify_recovered_preferences() "
    "end to end.",
    [3163667, 3336097, 3971252],
)

# ---------------------------------------------------------------- encryption / sensitive data
C(
    69142,
    "STRONG",
    BROWSER + "browser_settings_turn_on_scheduled_backups.js; "
    "browser_settings_enable_backup_encryption.js; "
    + XPC
    + "test_ArchiveEncryption.js; "
    "test_ArchiveEncryptionState.js",
    "test_turn_on_scheduled_backups_encryption and test_enable_backup_encryption_checkbox_confirm "
    "drive the same 'Back up your sensitive data' + password flow; the xpcshell pair covers the "
    "archive actually being encrypted.",
    [3163606, 3336039, 3971160],
)
C(
    69142,
    "STRONG",
    BROWSER + "browser_settings_turn_on_scheduled_backups.js; "
    "browser_settings_turn_off_scheduled_backups.js",
    "test_turn_on_scheduled_backups_confirm covers enabling backup with the sensitive-data box "
    "unchecked; test_turn_off_scheduled_backups_disables_encryption covers the unencrypted end "
    "state.",
    [3165757, 3336040, 3971161],
)
C(
    69142,
    "STRONG",
    XPC + "test_BackupService_enable_disable_encryption.js; "
    "test_CredentialsAndSecurityBackupResource.js; " + MAR + "test_backup.py",
    "The 'sensitive data is excluded from an unencrypted archive' rule is asserted for both the "
    "credentials and the autofill payload -- exactly what these negative cases check in "
    "about:logins and about:preferences.",
    [3199137, 3336056, 3971187, 3199136, 3336072, 3971208, 3198633, 3336074, 3971210],
)
C(
    69142,
    "STRONG",
    BROWSER
    + "browser_password_validation_inputs.js; "
    + BASE
    + "chrome/test_password_validation_inputs.html",
    "The password-input component tests assert the fields start masked and only reveal on the "
    "toggle, for both the sensitive-data modal and the change-password modal.",
    [3165765, 3336043, 3971164, 3165781, 3336044, 3971165],
)
C(
    69142,
    "STRONG",
    BROWSER
    + "browser_settings.js; browser_settings_turn_off_scheduled_backups.js; "
    + XPC
    + "test_BackupService_enable_disable_encryption.js",
    "test_disable_backup_encryption_confirm and test_turn_off_scheduled_backups_disables_encryption "
    "assert that clearing the sensitive-data checkbox tears down the stored password.",
    [3165788, 3336045, 3971166],
)
C(
    69142,
    "STRONG",
    BROWSER
    + "browser_settings_restore_from_backup.js; "
    + XPC
    + "test_BackupService_wrongPassword.js",
    "test_restore_from_backup sets a password on the archive and recovers with it; "
    "test_BackupService_wrongPassword.js covers the rejection path.",
    [3165985, 3336094, 3971241],
)

# ---------------------------------------------------------------- settings UI
C(
    69142,
    "STRONG",
    BROWSER + "browser_settings_turn_on_scheduled_backups.js; browser_settings.js; "
    "browser_settings_create_backup.js",
    "test_default_location_selected, test_no_default_folder and test_last_backup_info_and_location "
    "assert the default backup directory and the location readout in about:settings.",
    [3163630, 3336034, 3971155],
)
C(
    69142,
    "STRONG",
    BROWSER + "browser_settings_turn_on_scheduled_backups.js",
    "test_turn_on_custom_location_filepicker and test_embedded_component_persistent_data_filepicker "
    "drive the change-location filepicker and assert the new path is persisted.",
    [3163631, 3336035, 3971156],
)
C(
    69142,
    "STRONG",
    XPC + "test_BackupService.js",
    "test_deleteLastBackup_file_exists and test__deleteLastBackup_file_does_not_exist cover "
    "deleting the backup file from inside Firefox, including the already-gone case.",
    [3163632, 3336037, 3971158],
)
C(
    69142,
    "STRONG",
    BROWSER + "browser_settings_turn_off_scheduled_backups.js",
    "Both tasks assert deleteLastBackup is invoked when scheduled backups are turned off, so the "
    "archive does not survive the toggle.",
    [3165787, 3336046, 3971167],
)
C(
    69142,
    "STRONG",
    XPC
    + "test_BackupService_scheduler.js; "
    + BROWSER
    + "browser_settings_turn_on_scheduled_backups.js; browser_settings_create_backup.js",
    "The scheduler test covers a backup taken in response to profile activity; "
    "test_create_backup_on_enable / test_create_new_backup_trigger cover the immediate backup on "
    "enable.",
    [3166253, 3336047, 3971168],
)
C(
    69142,
    "STRONG",
    XPC
    + "test_BackupService_enabled.js; test_BackupService_enabledListPref.js; "
    + BROWSER
    + "browser_settings_turn_off_scheduled_backups.js",
    "Disabling the backup feature and the resulting service state is covered directly.",
    [3163599],
)

# ---------------------------------------------------------------- enterprise policies
C(
    69142,
    "STRONG",
    BROWSER + "browser_backup_policies.js",
    "test_backup_disabled_enterprise_policies, test_backup_archive_enabled_enterprise_policies, "
    "test_backup_restore_enabled_enterprise_policies and test_backup_service_disabled_enterprise_policies "
    "cover both the backup and the restore policy toggles.",
    [3171628, 3971301, 3171630, 3971303],
)

# ---------------------------------------------------------------- about:welcome restore page
C(
    69142,
    "STRONG",
    BROWSER + "browser_settings_restore_from_backup.js",
    "checkVisibleStatusTemplate() is driven with aboutWelcome:true, and "
    "test_restore_backup_file_info_display asserts the file-info block reporting whether the "
    "detected archive is encrypted.",
    [3200439, 3200880],
)
C(
    69142,
    "STRONG",
    BROWSER + "browser_settings_restore_from_backup.js",
    "test_restore_in_progress holds recovery unresolved and asserts the in-progress template is "
    "the visible one.",
    [3200881],
)
C(
    69142,
    "STRONG",
    BROWSER + "browser_settings_restore_from_backup.js",
    "test_error_about_welcome and test_restore_from_backup_displays_invalid_backup cover the "
    "corrupt/wrong-file error state; test_invalid_password_about_welcome covers the wrong-password "
    "error state.",
    [3200883, 3200887],
)
C(
    69142,
    "STRONG",
    BROWSER + "browser_settings_restore_from_backup.js",
    "test_support_links_non_embedded walks both the main support link and the incorrect-password "
    "link and asserts each resolves to its moz-support-link target.",
    [3200886, 3200888],
)
C(
    69142,
    "STRONG",
    "browser/components/aboutwelcome/tests/browser/browser_aboutwelcome_restore_backup.js; "
    + BROWSER
    + "browser_settings_restore_from_backup.js",
    "test_aboutwelcome_embedded_backup_restore_properties asserts the restore screen is what "
    "about:welcome renders when a backup is present, replacing the standard first-run content.",
    [3171571],
)
C(
    69142,
    "STRONG",
    BROWSER + "browser_settings_restore_from_backup.js",
    "test_restore_from_backup_prefills_prior_valid_backup and test_restore_uses_matching_initial_folder "
    "cover offering the detected archive; test_restore_fails_without_backup_in_state covers not "
    "offering it when none exists.",
    [3171568, 3171570],
)

# ---------------------------------------------------------------- restore scenarios
C(
    69142,
    "STRONG",
    MAR + "test_backup.py",
    "Create-then-recover on one machine is precisely what test_backup.py does.",
    [3165906, 3336093, 3971240],
)
C(
    69142,
    "STRONG",
    MAR
    + "test_backup_legacy_to_selectable.py; test_backup_replace_current_profile.py; "
    + XPC
    + "test_BackupService_recoverFromSnapshotFolderIntoSelectableProfile.js",
    "The legacy-profile-to-selectable-profile path, including renaming the existing profile and "
    "creating the new one, is covered end to end.",
    [3163598, 3336075, 3971214],
)
C(
    69142,
    "STRONG",
    MAR + "test_backup.py; " + BROWSER + "browser_settings_restore_from_backup.js",
    "Back up from about:settings and restore, encrypted and unencrypted, to a local directory -- "
    "both halves of the no-OneDrive matrix.",
    [3224164, 3336106, 3971263, 3224165, 3336107, 3971264],
)

# ---------------------------------------------------------------- reviewed but kept
C(
    69142,
    "MEDIUM",
    XPC + "test_PlacesBackupResource.js; " + MAR + "test_backup.py",
    "Favicons are archived, but nothing checks the icon renders in the URL bar, Library and "
    "History sidebar. Downloads ride along in places.sqlite but no test opens about:downloads "
    "after a restore.",
    [3163626, 3336031, 3971151, 3163619, 3336027, 3971146],
)
C(
    69142,
    "MEDIUM",
    XPC + "test_AddonsBackupResource.js; test_PreferencesBackupResource.js; "
    "test_SelectableProfileBackupResource.js",
    "Add-ons, themes, avatars and toolbar customisation are covered only as archived payload on "
    "disk -- never re-checked at the UI level (about:addons, the Extensions panel, the applied "
    "theme, the restored toolbar layout).",
    [
        3163656,
        3336068,
        3971204,
        3163642,
        3336059,
        3971189,
        3341224,
        3971190,
        3341298,
        3971191,
        3341329,
        3971192,
        3341330,
        3971193,
        3371359,
        3971194,
    ],
)
C(
    69142,
    "MEDIUM",
    XPC + "test_BackupService_onedrive.js",
    "OneDrive is only exercised against a mocked sign-in state in xpcshell. Picking a real "
    "connected OneDrive folder, detecting a backup there, and the OneDrive half of the "
    "backup+restore matrix all need a real account.",
    [3165702, 3336036, 3171569, 3224162, 3336104, 3971261, 3224163, 3336105, 3971262],
)
C(
    69142,
    "MEDIUM",
    XPC
    + "test_ArchiveEncryptionState.js; test_BackupService_enable_disable_encryption.js",
    "Encryption state can be replaced in xpcshell, but no test changes the password and then "
    "recovers an archive written under the new password.",
    [3165986, 3336095, 3971242],
)
C(
    69142,
    "MEDIUM",
    MAR
    + "test_backup_selectable_to_selectable.py; "
    + XPC
    + "test_BackupService_recoverFromSnapshotFolderIntoSelectableProfile.js; "
    "test_BackupService_crossProfileTypeRecovery.js; test_backup_replace_current_profile.py",
    "Recovery into a profile-managed install is covered, but the multi-profile disambiguation "
    "chooser and its explicit 'replace' choice are not asserted; nor is the post-restore claim "
    "that the old windows are gone.",
    [3336090, 3971237, 3381422, 3971245, 3202699, 3202701],
)
C(
    69142,
    "MEDIUM",
    MAR + "test_backup.py",
    "Nothing drives the onboarding-message entry point to backup, the terminal states of the "
    "about:welcome restore screen (Don't restore, success modal, set-default / pin-to-taskbar, "
    "dismiss), most-recent-archive auto-selection, or the macOS/Linux feature gating.",
    [
        3224154,
        3224158,
        3224160,
        3224161,
        3224166,
        3200889,
        3171575,
        3171576,
        3171577,
        3201769,
        3174471,
    ],
)
C(
    69142,
    "MEDIUM",
    "n/a",
    "Two-machine flows (write the archive on machine A, recover on machine B) and RTL visual "
    "inspection of the Backup pane and restore dialogs. 3971238 and 3971244 are already flagged "
    "[DELETE ME] in TestRail.",
    [
        3163603,
        3336092,
        3971239,
        3165796,
        3381419,
        3971244,
        3165815,
        3336091,
        3971238,
        3163595,
        3336086,
        3971225,
        3239129,
        3336087,
        3971226,
    ],
)
