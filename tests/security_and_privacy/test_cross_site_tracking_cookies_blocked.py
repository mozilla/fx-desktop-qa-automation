from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import AboutPrefs, GenericPage


@pytest.fixture()
def test_case():
    return "446402"


FIRST_TRACKER_WEBSITE = (
    "https://senglehardt.com/test/trackingprotection/test_pages/"
    "tracking_protection.html"
)
DETECTED_COOKIES = (
    "https://ads-track-digest256.dummytracker.org",
    "https://social-track-digest256.dummytracker.org",
    "https://analytics-track-digest256.dummytracker.org",
)


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("privacy.trackingprotection.pbmode.enabled", False),
        ("privacy.trackingprotection.cryptomining.enabled", False),
        ("privacy.trackingprotection.fingerprinting.enabled", False),
        ("privacy.fingerprintingProtection.pbmode", False),
    ]


def test_cross_site_tracking_cookies_blocked(
    driver: Firefox, about_prefs_privacy: AboutPrefs, trust_panel: TrustPanel
):
    """
    C446402: Ensures the cross tracking cookies are displayed in the tracker panel
    """
    # instantiate objects
    about_prefs_privacy.open()
    about_prefs_privacy.select_trackers_to_block(
        "cookies-checkbox", "cookies-isolate-social-media-option"
    )
    GenericPage(driver, url=FIRST_TRACKER_WEBSITE).open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    trust_panel.trackers_blocked("tracking-cookies")
    trust_panel.trackers_detected("tracking-content")
    trust_panel.sites_blocked(DETECTED_COOKIES)
    trust_panel.sites_detected(DETECTED_COOKIES)
