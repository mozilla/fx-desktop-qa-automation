from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TrackerPanel
from modules.page_object import AboutPrefs, GenericPage

CRYPTOMINERS_URL = "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting_and_cryptomining.html"


def test_blocking_cryptominers(driver: Firefox):
    """C450232 - Cryptominers are blocked and shown in Standard mode in the Information panel"""
    # instantiate objects
    nav = Navigation(driver).open()
    about_prefs = AboutPrefs(driver, category="privacy").open()
    tracker_panel = TrackerPanel(driver)
    tracking_page = GenericPage(driver, url=CRYPTOMINERS_URL)

    # Select custom option and keep just cryptominers checked
    about_prefs.get_element("custom-radio").click()
    about_prefs.get_element("cookies-checkbox").click()
    about_prefs.get_element("tracking-checkbox").click()
    about_prefs.get_element("known-fingerprints-checkbox").click()
    about_prefs.get_element("suspected-fingerprints-checkbox").click()

    # Access url and click on the shield icon and verify that cryptominers are blocked
    tracking_page.open()
    tracker_panel.wait_for_blocked_tracking_icon(nav, tracking_page)
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("shield-icon").click()
        assert nav.get_element("cryptominers").is_displayed()
