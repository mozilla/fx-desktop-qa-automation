import time

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TrustPanel
from modules.page_object import AboutPrefs, GenericPage


@pytest.fixture()
def test_case():
    return "446403"


CRYPTOMINERS_URL = "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting_and_cryptomining.html"


def test_blocking_cryptominers(
    driver: Firefox,
    nav: Navigation,
    about_prefs_privacy: AboutPrefs,
    trust_panel: TrustPanel,
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
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()
    # time.sleep(200)
    trust_panel.trackers_blocked("cryptominer")
