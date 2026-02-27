from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TrackerPanel
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "446393"


TRACKER_URL = "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting_and_cryptomining_and_cookies.html"


def test_cross_site_trackrs_crypto_fingerprinter_blocked(
    driver: Firefox, tracker_panel: TrackerPanel, nav: Navigation
):
    """
    C446393: Ensures that some trackers are blocked on certain website
    """
    # instantiate objs
    tracker_page = GenericPage(driver, url=TRACKER_URL)

    # wait for the shield icon
    tracker_page.open()
    tracker_panel.open_panel()
    tracker_panel.wait_for_trackers()
    tracker_panel.trackers_detected("tracking-content")
    tracker_panel.trackers_blocked("tracking-cookies", "cryptominer")
