import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TrackerPanel
from modules.page_object import AboutPrefs, GenericPage


@pytest.fixture()
def test_case():
    return "446403"


CRYPTOMINERS_URL = "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting_and_cryptomining.html"


def test_blocking_cryptominers(
    driver: Firefox,
    nav: Navigation,
    about_prefs_privacy: AboutPrefs,
    tracker_panel: TrackerPanel,
):
    """
    C446403 - Cryptominers are blocked and shown in Standard mode in the Information panel
    """
    # instantiate objects
    tracking_page = GenericPage(driver, url=CRYPTOMINERS_URL)

    about_prefs_privacy.open()

    # Select custom option and keep just cryptominers checked
    about_prefs_privacy.select_trackers_to_block("cryptominers-checkbox")

    # Access url and click on the shield icon and verify that cryptominers are blocked
    tracking_page.open()
    tracker_panel.wait_for_blocked_tracking_icon(nav, tracking_page)
    nav.assert_blocked_trackers("cryptominers")
