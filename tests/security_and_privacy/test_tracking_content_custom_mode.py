import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TrustPanel
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3054912"


TRACKER_URL = "https://senglehardt.com/test/trackingprotection/test_pages/tracking_protection.html"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("network.cookie.cookieBehavior", 0),
        ("privacy.trackingprotection.pbmode.enabled", False),
        ("privacy.trackingprotection.cryptomining.enabled", False),
        ("privacy.trackingprotection.fingerprinting.enabled", False),
        ("privacy.fingerprintingProtection.pbmode", False),
    ]


def test_blocked_tracking_content(
    driver: Firefox,
    nav: Navigation,
    trust_panel: TrustPanel,
    about_prefs_privacy: AboutPrefs,
):
    """
    C446405.1: Ensure that ETP Custom mode with option Tracking Content -> In all windows set
    blocks tracking content
    """
    about_prefs_privacy.open()
    about_prefs_privacy.select_trackers_to_block(
        "tracking-checkbox", "tracking-in-all-windows"
    )
    driver.get(TRACKER_URL)

    trust_panel.open_panel()
    trust_panel.wait_for_trackers()
    trust_panel.trackers_blocked("tracking-content")


def test_allowed_tracking_content(
    driver: Firefox,
    nav: Navigation,
    trust_panel: TrustPanel,
    about_prefs_privacy: AboutPrefs,
):
    """
    C446405.2: Ensure that ETP Custom mode w/ option Tracking Content -> Only in Private Windows set
    allows tracking content
    """

    about_prefs_privacy.open()
    about_prefs_privacy.select_trackers_to_block("tracking-checkbox")

    driver.get(TRACKER_URL)

    trust_panel.open_panel()
    trust_panel.wait_for_trackers()
    trust_panel.trackers_detected("tracking-content")
