import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs

ETP_TITLE = "Enhanced Tracking Protection"
# The brand name sits in the middle of the ETP message and changes per channel,
# so the message is checked as the two halves surrounding it.
ETP_MESSAGE_START = "Sites use trackers to follow you online and show creepy ads."
ETP_STATUS_MESSAGE_END = (
    "shields you as you browse, blocking trackers automatically so you’re in control "
    "of your digital trail."
)
ETP_ADVANCED_MESSAGE_END = (
    "shields you as you browse, blocking most trackers automatically so you’re in "
    "control of your digital trail."
)

ADVANCED_SETTINGS_TITLE = "Advanced settings"

STANDARD_LABEL = "Standard (default)"
STANDARD_DESCRIPTION = (
    "Strong, reliable protections that work smoothly with most websites."
)
STRICT_LABEL = "Strict"
MAJOR_ISSUES_LABEL = "Fix major site issues (recommended)"
MAJOR_ISSUES_DESCRIPTION = (
    "Helps load sites and features by unblocking only essential elements that may "
    "contain trackers. Covers most common problems."
)
MINOR_ISSUES_LABEL = "Fix minor site issues"
MINOR_ISSUES_DESCRIPTION = (
    "Restores things like videos in an article or comment sections by unblocking "
    "elements that may contain trackers. This can reduce site issues but offers less "
    "protection. Must be used with fixes for major issues."
)
CUSTOM_LABEL = "Custom"
CUSTOMIZE_TITLE = "Customize tracking protection"

TRACKING_PROTECTION_TITLE = "Tracking protection"
TRACKING_PROTECTION_DESCRIPTION = "Choose which protections to turn on or off."
COOKIES_LABEL = "Cookies"
# Firefox hides two more cookie options behind a pref, so these are the ones that
# always have to be on offer.
COOKIE_OPTIONS = [
    "Allow all cookies",
    "Isolate cross-site cookies",
    "Block all cross-site cookies (may cause websites to break)",
    "Block all cookies (will cause websites to break)",
]
TRACKING_CONTENT_LABEL = "Tracking content"
CONTEXT_OPTIONS = ["In all windows", "Only in private windows"]
CRYPTOMINERS_LABEL = "Cryptominers"
KNOWN_FINGERPRINTERS_LABEL = "Known fingerprinters"
SUSPECTED_FINGERPRINTERS_LABEL = "Suspected fingerprinters"

RESET_TITLE = "Reset customizations"
RESET_DESCRIPTION = "Restore settings to a preset protection level."
RESET_STANDARD_LABEL = "Reset to standard"
RESET_STRICT_LABEL = "Reset to strict"
RELOAD_TABS_MESSAGE = "Reload your tabs to apply these changes."
RELOAD_TABS_LABEL = "Reload all tabs"


@pytest.fixture()
def test_case():
    return "446318"


@pytest.fixture()
def add_to_prefs_list():
    """
    Geckodriver's profile turns tracking protection off in private windows, which
    leaves ETP on "Custom". Put the profile back on the Standard defaults a fresh
    profile ships with.
    """
    return [
        ("browser.contentblocking.category", "standard"),
        ("privacy.trackingprotection.pbmode.enabled", True),
    ]


def test_verify_etp_section_display(driver: Firefox, about_prefs_privacy: AboutPrefs):
    """
    C446318 - Verify that the Enhanced Tracking Protection section from about:preferences#privacy is properly displayed
    """

    # Access about:preferences#privacy
    about_prefs_privacy.open()

    # The shield icon and the "Enhanced Tracking Protection" title is displayed
    about_prefs_privacy.element_visible("etp-status-shield-icon")
    about_prefs_privacy.element_attribute_is("etp-status-card", "label", ETP_TITLE)

    # The shield icon and the message: "Sites use trackers to follow you online and show creepy ads.
    # Nightly shields you as you browse, blocking trackers automatically so you’re in control of your digital trail
    about_prefs_privacy.element_attribute_contains(
        "etp-status-card", "description", ETP_MESSAGE_START
    )
    about_prefs_privacy.element_attribute_contains(
        "etp-status-card", "description", ETP_STATUS_MESSAGE_END
    )

    # The "Learn more" link is displayed
    about_prefs_privacy.element_visible("etp-status-learn-more")

    # The Standard section is selected
    about_prefs_privacy.element_attribute_is("etp-status-item", "label", STANDARD_LABEL)

    # Click `Advanced settings` to verify the "Enhanced Tracking Protection" card
    about_prefs_privacy.open_etp_settings()
    about_prefs_privacy.element_attribute_is("etp-page-header", "heading", ETP_TITLE)
    about_prefs_privacy.element_attribute_is(
        "etp-advanced-settings-card", "label", ADVANCED_SETTINGS_TITLE
    )
    about_prefs_privacy.element_attribute_contains(
        "etp-advanced-settings-card", "description", ETP_MESSAGE_START
    )
    about_prefs_privacy.element_attribute_contains(
        "etp-advanced-settings-card", "description", ETP_ADVANCED_MESSAGE_END
    )

    # The "Learn more" link is displayed
    about_prefs_privacy.element_visible("etp-advanced-settings-learn-more")

    # The Standard section is selected
    about_prefs_privacy.verify_etp_level("standard")

    # The `Strong, reliable protections that work smoothly with most websites.` message is displayed
    about_prefs_privacy.element_attribute_is(
        "etp-level-standard", "description", STANDARD_DESCRIPTION
    )

    # Click the "Strict" radio button and verify the strict section
    about_prefs_privacy.set_etp_level("strict")

    # The "Strict" radio button is selected
    about_prefs_privacy.verify_etp_level("strict")
    about_prefs_privacy.element_attribute_is("etp-level-strict", "label", STRICT_LABEL)

    # Fix major site issues (recommended) is checked containing the `Helps load sites and features by unblocking only
    # essential elements that may contain trackers. Covers most common problems` message. The 'Learn more' link
    about_prefs_privacy.element_visible("etp-major-issues-checkbox")
    about_prefs_privacy.verify_etp_exception_checkbox("major", checked=True)
    about_prefs_privacy.element_attribute_is(
        "etp-major-issues-checkbox", "label", MAJOR_ISSUES_LABEL
    )
    about_prefs_privacy.element_attribute_is(
        "etp-major-issues-checkbox", "description", MAJOR_ISSUES_DESCRIPTION
    )
    about_prefs_privacy.element_visible("etp-major-issues-learn-more")

    # Fix minor site issues is unchecked, containing the `Restores things like videos in an article or comment
    # sections by unblocking elements that may contain trackers. This can reduce site issues but offers less protection.
    # Must be used with fixes for major issues.` message
    about_prefs_privacy.element_visible("etp-minor-issues-checkbox")
    about_prefs_privacy.verify_etp_exception_checkbox("minor", checked=False)
    about_prefs_privacy.element_attribute_is(
        "etp-minor-issues-checkbox", "label", MINOR_ISSUES_LABEL
    )
    about_prefs_privacy.element_attribute_is(
        "etp-minor-issues-checkbox", "description", MINOR_ISSUES_DESCRIPTION
    )

    # Click on the Custom radio button and Customize tracking protection
    about_prefs_privacy.set_etp_level("custom")
    about_prefs_privacy.verify_etp_level("custom")
    about_prefs_privacy.element_attribute_is("etp-level-custom", "label", CUSTOM_LABEL)
    about_prefs_privacy.element_attribute_is(
        "etp-customize-button", "label", CUSTOMIZE_TITLE
    )

    # Selecting the "Customize tracking protection" will open the about:preferences#etpCustomize page
    # "Tracking protection"
    about_prefs_privacy.open_etp_customize()
    about_prefs_privacy.expect(
        lambda driver: driver.current_url == "about:preferences#etpCustomize"
    )
    about_prefs_privacy.element_attribute_is(
        "etp-customize-page-header", "heading", CUSTOMIZE_TITLE
    )
    about_prefs_privacy.element_attribute_is(
        "etp-customize-card", "label", TRACKING_PROTECTION_TITLE
    )

    # The "Choose which protections to turn on or off" message is displayed
    about_prefs_privacy.element_attribute_is(
        "etp-customize-card", "description", TRACKING_PROTECTION_DESCRIPTION
    )

    # Fix major site issues (recommended) is displayed as checked
    about_prefs_privacy.element_visible("etp-customize-major-issues-checkbox")
    about_prefs_privacy.verify_etp_exception_checkbox(
        "major", checked=True, pane="etpCustomize"
    )
    about_prefs_privacy.element_attribute_is(
        "etp-customize-major-issues-checkbox", "label", MAJOR_ISSUES_LABEL
    )
    about_prefs_privacy.element_attribute_is(
        "etp-customize-major-issues-checkbox", "description", MAJOR_ISSUES_DESCRIPTION
    )
    about_prefs_privacy.element_visible("etp-customize-major-issues-learn-more")

    # Fix minor site issues is displayed as unchecked
    about_prefs_privacy.element_visible("etp-customize-minor-issues-checkbox")
    about_prefs_privacy.verify_etp_exception_checkbox(
        "minor", checked=False, pane="etpCustomize"
    )
    about_prefs_privacy.element_attribute_is(
        "etp-customize-minor-issues-checkbox", "label", MINOR_ISSUES_LABEL
    )
    about_prefs_privacy.element_attribute_is(
        "etp-customize-minor-issues-checkbox", "description", MINOR_ISSUES_DESCRIPTION
    )

    # Cookies toggle button with dropdown options
    about_prefs_privacy.element_visible("etp-custom-cookies-toggle")
    about_prefs_privacy.verify_etp_custom_toggle("cookies-checkbox", pressed=True)
    about_prefs_privacy.element_attribute_is(
        "etp-custom-cookies-toggle", "label", COOKIES_LABEL
    )
    about_prefs_privacy.element_visible("etp-custom-cookie-behavior")
    cookie_options = about_prefs_privacy.get_etp_custom_dropdown_options(
        "etp-custom-cookie-behavior-select"
    )
    assert set(COOKIE_OPTIONS).issubset(cookie_options), (
        f"Missing cookie blocking options, found {cookie_options}"
    )

    # Tracking content toggle button with dropdown options
    about_prefs_privacy.element_visible("etp-custom-tracking-toggle")
    about_prefs_privacy.verify_etp_custom_toggle("tracking-checkbox", pressed=True)
    about_prefs_privacy.element_attribute_is(
        "etp-custom-tracking-toggle", "label", TRACKING_CONTENT_LABEL
    )
    about_prefs_privacy.element_visible("etp-custom-tracking-context")
    tracking_options = about_prefs_privacy.get_etp_custom_dropdown_options(
        "etp-custom-tracking-context-select"
    )
    assert tracking_options == CONTEXT_OPTIONS, (
        f"Unexpected tracking content window options: {tracking_options}"
    )

    # Cryptominers toggle button
    about_prefs_privacy.element_visible("etp-custom-cryptomining-toggle")
    about_prefs_privacy.verify_etp_custom_toggle("cryptominers-checkbox", pressed=True)
    about_prefs_privacy.element_attribute_is(
        "etp-custom-cryptomining-toggle", "label", CRYPTOMINERS_LABEL
    )

    # Known fingerprinters toggle button
    about_prefs_privacy.element_visible("etp-custom-known-fingerprinting-toggle")
    about_prefs_privacy.verify_etp_custom_toggle(
        "known-fingerprints-checkbox", pressed=True
    )
    about_prefs_privacy.element_attribute_is(
        "etp-custom-known-fingerprinting-toggle", "label", KNOWN_FINGERPRINTERS_LABEL
    )

    # Suspected fingerprinters toggle button
    about_prefs_privacy.element_visible("etp-custom-suspect-fingerprinting-toggle")
    about_prefs_privacy.verify_etp_custom_toggle(
        "suspected-fingerprints-checkbox", pressed=True
    )
    about_prefs_privacy.element_attribute_is(
        "etp-custom-suspect-fingerprinting-toggle",
        "label",
        SUSPECTED_FINGERPRINTERS_LABEL,
    )
    about_prefs_privacy.element_visible("etp-custom-suspect-fingerprinting-context")
    suspected_options = about_prefs_privacy.get_etp_custom_dropdown_options(
        "etp-custom-suspect-fingerprinting-context-select"
    )
    assert suspected_options == CONTEXT_OPTIONS, (
        f"Unexpected suspected fingerprinters window options: {suspected_options}"
    )

    # The reset customizations option is displayed. The 'Reload all tabs' button is displayed on the ETP switch.
    about_prefs_privacy.element_attribute_is("etp-reset-card", "label", RESET_TITLE)
    about_prefs_privacy.element_attribute_is(
        "etp-reset-card", "description", RESET_DESCRIPTION
    )
    about_prefs_privacy.element_visible("etp-reset-standard-button")
    about_prefs_privacy.element_attribute_is(
        "etp-reset-standard-button", "label", RESET_STANDARD_LABEL
    )
    about_prefs_privacy.element_visible("etp-reset-strict-button")
    about_prefs_privacy.element_attribute_is(
        "etp-reset-strict-button", "label", RESET_STRICT_LABEL
    )
    about_prefs_privacy.element_visible("etp-customize-reload-tabs-hint")
    about_prefs_privacy.element_attribute_is(
        "etp-customize-reload-tabs-hint", "message", RELOAD_TABS_MESSAGE
    )
    about_prefs_privacy.element_visible("etp-customize-reload-tabs-button")
    about_prefs_privacy.element_attribute_is(
        "etp-customize-reload-tabs-button", "label", RELOAD_TABS_LABEL
    )
