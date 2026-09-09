"""Critical round -- Easy Setup onboarding (suite 23035).

155 critical cases over 62 sections, but only 47 distinct flows: the suite re-states the same
about:welcome slides once per platform and per entry point. Clusters are therefore keyed by
title.

The tree's browser/components/aboutwelcome/tests/browser/ directory tracks this feature
closely -- there is a test per slide (language switcher, mobile downloads, addons picker,
gratitude, import, theme picker) plus dedicated telemetry tests. The consistent exception is
the "UI - Light Theme" rows: those enumerate layout, imagery, exact copy and colour, which the
tree does not assert.
"""

from c_util import CT

AW = "browser/components/aboutwelcome/tests/browser/"
MIG = "browser/components/migration/tests/browser/"

# ---------------------------------------------------------------- telemetry / pings
CT(
    23035,
    "STRONG",
    AW + "browser_aboutwelcome_glean.js; browser_aboutwelcome_multistage_mr.js; "
    "browser_aboutwelcome_impression_action.js; browser_aboutwelcome_multistage_default.js",
    "test_welcome_telemetry and test_aboutwelcome_easy_setup_screen_impression assert the "
    "messaging-system impression ping is emitted for the Easy Setup screen with the expected "
    "fields; test_send_aboutwelcome_as_page_in_event_telemetry covers the page attribution "
    "these cases read off the ping.",
    [
        "Easy Setup - Impression Ping",
        "Glean - Setup",
    ],
)
CT(
    23035,
    "STRONG",
    AW + "browser_aboutwelcome_glean.js; browser_aboutwelcome_impression_action.js; "
    "browser_aboutwelcome_multistage_default.js",
    "test_allowlisted_impression_action_fires_once, test_multi_action_impression_fires and "
    "test_welcome_telemetry cover the click-side pings for the primary button and the sign-in "
    "hyperlink, including the multi-select payload.",
    [
        'Easy Setup - Click the "Sign in" hyperlink - Telemetry',
        "Easy Setup - Click the primary button while all options are checked - Telemetry",
        "Easy Setup - Click the primary button while both options are checked - Telemetry",
        "Easy Setup - Click the primary button with the option checked - Telemetry",
    ],
)
CT(
    23035,
    "STRONG",
    AW + "browser_aboutwelcome_glean.js; browser_aboutwelcome_impression_action.js; "
    "browser_aboutwelcome_multistage_languageSwitcher.js; browser_aboutwelcome_mobile_downloads.js; "
    "browser_aboutwelcome_multistage_addonspicker.js; browser_aboutwelcome_multistage_mr.js",
    "The per-slide impression pings ride the same messaging-system path that "
    "test_welcome_telemetry and test_allowlisted_impression_action_fires_once assert, and each "
    "of these slides has its own test that renders it so the impression is generated.",
    [
        "Choose Your Language Slide - Impression Ping",
        "Mobile Cross-Promotion Slide - Impression Ping",
        "Introduce AMO - Impression Ping",
        "MR Gratitude Slide - Impression Ping",
        "Import Browser Data - Impression ping",
        "Import Browser Data - Click ping",
    ],
)

# ---------------------------------------------------------------- Easy Setup slide
CT(
    23035,
    "STRONG",
    AW + "browser_aboutwelcome_fxa_signin_flow.js",
    "Nine tasks cover the sign-in flow launched from about:welcome -- success, success with a "
    "service parameter, abort, the separate sign-in window, multiple tabs, and the entrypoint "
    "UTM parameters.",
    ["Easy Setup - Functionality - Sign in with a new Firefox account"],
)
CT(
    23035,
    "STRONG",
    AW + "browser_aboutwelcome_multiselect.js; browser_aboutwelcome_multistage_mr.js; "
    "browser_aboutwelcome_multistage_default.js",
    "test_aboutwelcome_multiselect and test_multiselect_with_item_description drive the Easy "
    "Setup checkbox set and assert the actions that fire when the primary button is pressed "
    "with the options checked; test_AWMultistage_Primary_Action covers the button itself.",
    [
        "Easy Setup - Functionality - Click the primary button while all options are checked",
        "Easy Setup - Functionality - Click the primary button while both options are checked",
        "Easy Setup - Functionality - Click the primary button with the option checked",
    ],
)

# ---------------------------------------------------------------- pin / default browser matrix
CT(
    23035,
    "STRONG",
    AW
    + "browser_aboutwelcome_upgrade_multistage_mr.js; browser_aboutwelcome_multistage_default.js; "
    "browser_aboutwelcome_screen_targeting.js",
    "test_aboutwelcome_upgrade_mr_private_pin, test_aboutwelcome_upgrade_mr_private_pin_get_started "
    "and test_aboutwelcome_upgrade_mr_private_pin_not_needed drive exactly this matrix -- which "
    "screen is shown for each combination of already-pinned and already-default -- and "
    "browser_aboutwelcome_screen_targeting.js covers the targeting that selects it.",
    [
        "Firefox is NOT pinned and NOT the default browser",
        "Firefox IS pinned and NOT the default browser",
        "Firefox is NOT pinned and IS set as the default browser",
        "Firefox IS pinned and it IS the default browser",
        "Firefox is NOT the default browser",
        "Firefox IS the default browser",
    ],
)

# ---------------------------------------------------------------- Choose Your Language slide
CT(
    23035,
    "STRONG",
    AW + "browser_aboutwelcome_multistage_languageSwitcher.js",
    "test_aboutwelcome_languageSwitcher_MR covers the slide being triggered on a language "
    "mismatch, test_aboutwelcome_languageSwitcher_noMatch covers it correctly *not* appearing "
    "when the locales already agree, and test_aboutwelcome_languageSwitcher_accept drives the "
    "'Switch to [system language]' button through to the applied locale.",
    [
        "Choose Your Language slide - Trigger",
        "Choose Your Language Slide - Trigger",
        "Choose Your Language Slide - No language mismatch - doesn't appear",
        'Choose Your Language Slide - Functionality - "Switch to [system language]" button',
        'Choose Your Language slide - Click the "Switch to [system language]" button',
    ],
)

# ---------------------------------------------------------------- Mobile cross-promotion slide
CT(
    23035,
    "STRONG",
    AW
    + "browser_aboutwelcome_mobile_downloads.js; browser_aboutwelcome_multistage_default.js",
    "test_aboutwelcome_mobile_downloads_qr asserts the QR code is rendered with the expected "
    "download link, test_aboutwelcome_mobile_downloads_all covers the whole slide, and "
    "test_AWMultistage_Secondary_Open_URL_Action covers the skip/secondary button advancing "
    "the flow.",
    [
        "Mobile Cross-Promotion Slide - Scan the QR code",
        'Mobile Cross-Promotion Slide - Functionality - "Skip this step" button',
        'Mobile Cross-Promotion Slide - Click the "Skip this step" button',
    ],
)

# ---------------------------------------------------------------- Introduce AMO slide
CT(
    23035,
    "STRONG",
    AW
    + "browser_aboutwelcome_multistage_addonspicker.js; browser_aboutwelcome_rtamo.js; "
    "browser_aboutwelcome_multistage_default.js",
    "test_aboutwelcome_addonspicker renders the add-ons picker screen and drives its actions; "
    "test_AMO_untranslated_strings covers the AMO screen strings and "
    "test_AWMultistage_Secondary_Open_URL_Action the 'explore recommended add-ons' navigation.",
    [
        'Introduce AMO - Click the "Explore our recommended add-ons" button',
        'Introduce AMO - Click the "Explore staff recommended add-ons"',
    ],
)

# ---------------------------------------------------------------- Gratitude slide
CT(
    23035,
    "STRONG",
    AW + "browser_aboutwelcome_multistage_mr.js",
    "test_aboutwelcome_gratitude renders the gratitude screen and asserts the 'Start browsing' "
    "primary action closes the flow.",
    [
        'MR Gratitude Slide - "Start browsing" button',
        'MR Gratitude Slide - Functionality - "Start browsing" button',
    ],
)

# ---------------------------------------------------------------- Import browser data slides
CT(
    23035,
    "STRONG",
    AW + "browser_aboutwelcome_import.js; browser_aboutwelcome_multistage_default.js; "
    "browser_aboutwelcome_multistage_mr.js; "
    + MIG
    + "browser_aboutwelcome_behavior.js; "
    "browser_do_migration.js",
    "test_AWMultistage_Import and test_wait_import_modal / test_wait_import_spotlight drive the "
    "Import button from about:welcome; test_aboutwelcome_embedded_migration covers the embedded "
    "migration wizard, and browser_do_migration.js asserts the migration completes and reports "
    "success -- which is what the 'Data Imported Successfully' rows check.",
    [
        'Import Data Slide - Functionality - Click the "Import" button',
        'Import Data Slide - Functionality - Click the "Continue" button from the "Data Imported Successfully" Slide',
        "Import Browser Data - Data Imported Successfully",
        'Data Imported Successfully - Click the "Continue" button',
    ],
)

# ---------------------------------------------------------------- upgrade spotlight
CT(
    23035,
    "STRONG",
    AW
    + "browser_aboutwelcome_upgrade_multistage_mr.js; browser_aboutwelcome_nimbus_gate.js; "
    "browser_aboutwelcome_screen_targeting.js",
    "test_aboutwelcome_upgrade_mr_prefs_off asserts the upgrade experience is suppressed when "
    "its prefs are off, and the nimbus-gate / targeting tests cover the conditions under which "
    "the spotlight is or is not shown after an update.",
    ["Verify that the Upgrade spotlight is not displayed after a browser update"],
)

# ---------------------------------------------------------------- reviewed but kept
CT(
    23035,
    "MEDIUM",
    AW
    + "browser_aboutwelcome_multistage_default.js; browser_aboutwelcome_configurable_ui.js; "
    "browser_aboutwelcome_theme_picker.js",
    "The 'UI - Light Theme' rows are visual-layout checks: split background, which side the "
    "Firefox logo sits on, the exact bold title copy, colours and imagery. "
    "test_multistage_aboutwelcome_default asserts the expected elements exist on each screen, "
    "which overlaps the structure but not the appearance these cases exist to catch.",
    [
        "Easy Setup - UI - Light Theme",
        "Choose Your Language Slide - UI - Light Theme",
        "Mobile Cross-Promotion Slide - UI - Light Theme",
        "Introduce AMO - UI",
        "MR Gratitude Slide - UI - Light Theme",
        "Import Browser Data First Slide - UI - Light theme",
        "Loading Data Slide - UI - Light theme",
        "Data Imported Successfully - UI",
    ],
)
CT(
    23035,
    "MEDIUM",
    AW
    + "browser_aboutwelcome_theme_picker.js; browser_aboutwelcome_multistage_default.js",
    "test_aboutwelcome_theme_picker_screen_displays and test_AWMultistage_Themes cover the theme "
    "picker screen and applying a theme, but nothing re-renders the about:welcome screens under "
    "the dark theme and checks they display correctly.",
    [
        'Verify that the "about:welcome" screens are correctly displayed with dark theme enabled'
    ],
)
