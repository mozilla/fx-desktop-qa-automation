from time import sleep

from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_about_prefs import AboutPrefs

CRYPTOMINERS_URL = "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting_and_cryptomining.html"


def test_blocking_cryptominers(driver: Firefox):
    # instantiate objects
    nav = Navigation(driver).open()
    about_prefs = AboutPrefs(driver, category="privacy").open()

    # Select custom option and keep just cryptominers checked
    about_prefs.get_element("custom-radio").click()
    about_prefs.get_element("cookies-checkbox").click()
    about_prefs.get_element("tracking-checkbox").click()
    about_prefs.get_element("known-fingerprints-checkbox").click()
    about_prefs.get_element("suspected-fingerprints-checkbox").click()
    sleep(2)

    # Access url and click on the shield icon and verify that cryptominers are blocked
    driver.get(CRYPTOMINERS_URL)
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("shield-icon").click()
        assert nav.get_element("cryptominers").is_displayed()
