import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TrackerPanel
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "450232"


CRYPTOMINERS_URL = "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting_and_cryptomining.html"


def test_cryptominers_blocked_and_shown_in_info_panel(
    driver: Firefox, tracker_panel: TrackerPanel
):
    """
    C450232: Cryptominers are blocked and shown in Standard mode in the Information pannel
    """
    tracking_page = GenericPage(driver, url=CRYPTOMINERS_URL)
    tracking_page.open()
    tracker_panel.open_panel()
    tracker_panel.wait_for_trackers()
    tracker_panel.trackers_blocked("cryptominer")
