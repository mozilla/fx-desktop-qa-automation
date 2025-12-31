import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TrackerPanel
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "446402"


FIRST_TRACKER_WEBSITE = "https://senglehardt.com/test/trackingprotection/test_pages/tracking_protection.html"
ALLOWED_COOKIES = set(
    [
        "https://ads-track-digest256.dummytracker.org",
        "https://social-track-digest256.dummytracker.org",
        "https://analytics-track-digest256.dummytracker.org",
    ]
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
    driver: Firefox, nav: Navigation, tracker_panel: TrackerPanel
):
    """
    C446402: Ensures the cross tracking cookies are displayed in the tracker panel
    """
    # instantiate objects
    tracker_website = GenericPage(driver, url=FIRST_TRACKER_WEBSITE).open()
    tracker_panel.wait_for_trackers(nav, tracker_website)

    nav.open_tracker_panel()

    # fetch the items in the cross site trackers and verify
    cross_site_trackers = tracker_panel.open_and_return_cross_site_trackers()
    nav.verify_cross_site_trackers(cross_site_trackers, ALLOWED_COOKIES)
