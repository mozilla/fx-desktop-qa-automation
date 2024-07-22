from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TrackerPanel
from modules.page_object import GenericPage

TRACKER_URL = "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting_and_cryptomining_and_cookies.html"


def test_cross_site_trackrs_crypto_fingerprinter_blocked(driver: Firefox):
    """
    C446393: Ensures that some trackers are blocked on certain website
    """
    tracker_page = GenericPage(driver, url=TRACKER_URL).open()
    tracker_panel = TrackerPanel(driver)
    nav = Navigation(driver)

    nav.open_tracker_panel()
