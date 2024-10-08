import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TrackerPanel
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "450232"


CRYPTOMINERS_URL = "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting_and_cryptomining.html"


def test_cryptominers_blocked_and_shown_in_info_panel(driver: Firefox):
    """
    C450232: Cryptominers are blocked and shown in Standard mode in the Information pannel
    """
    # Access URL, needed sleep otherwise cryptomining will be displayed as unblocked
    nav = Navigation(driver)
    tracking_page = GenericPage(driver, url=CRYPTOMINERS_URL)
    tracker_panel = TrackerPanel(driver)

    tracking_page.open()
    tracker_panel.wait_for_blocked_tracking_icon(nav, tracking_page)

    # Click on the shield icon and verify that cryptominers are blocked
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("shield-icon").click()
        assert nav.get_element("cryptominers").is_displayed()
