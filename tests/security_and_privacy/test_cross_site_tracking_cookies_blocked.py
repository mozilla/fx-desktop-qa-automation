from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TrackerPanel
from modules.page_object import GenericPage

FIRST_TRACKER_WEBSITE = "https://senglehardt.com/test/trackingprotection/test_pages/tracking_protection.html"
ALLOWED_TRACKING_URLS = set(
    [
        "https://content-track-digest256.dummytracker.org",
        "https://ads-track-digest256.dummytracker.org",
        "https://social-track-digest256.dummytracker.org",
        "https://analytics-track-digest256.dummytracker.org",
    ]
)


@pytest.fixture()
def add_prefs():
    return [
        ("network.cookie.cookieBehavior", 0),
        ("privacy.trackingprotection.pbmode.enabled", False),
        ("privacy.trackingprotection.cryptomining.enabled", False),
        ("privacy.trackingprotection.fingerprinting.enabled", False),
        ("privacy.fingerprintingProtection.pbmode", False),
    ]


def test_cross_site_tracking_cookies_blocked(driver: Firefox):
    """
    C446402: Ensures the
    """
    # instantiate objects
    nav = Navigation(driver)
    tracker_panel = TrackerPanel(driver)
    tracker_website = GenericPage(driver, url=FIRST_TRACKER_WEBSITE).open()
    tracker_panel.wait_for_trackers(nav, tracker_website)

    driver.set_context(driver.CONTEXT_CHROME)
    nav.open_tracker_panel()

    # # fetch the items in the cross site trackers
    cross_site_trackers = tracker_panel.open_and_return_cross_site_trackers()
    sleep(40)
