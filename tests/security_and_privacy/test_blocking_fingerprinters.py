from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "446404"


FINGERPRINTERS_URL = (
    "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting.html"
)


@pytest.mark.unstable
def test_blocking_fingerprinter(driver: Firefox):
    """
    C446404: Blocking Fingerprinters
    """
    # instantiate objects
    nav = Navigation(driver).open()
    about_prefs = AboutPrefs(driver, category="privacy").open()

    # Select custom option and keep just known fingerprinters checked
    about_prefs.get_element("custom-radio").click()
    about_prefs.get_element("cookies-checkbox").click()
    about_prefs.get_element("tracking-checkbox").click()
    about_prefs.get_element("cryptominers-checkbox").click()
    about_prefs.get_element("suspected-fingerprints-checkbox").click()
    sleep(2)

    # Access url and click on the shield icon and verify that known fingerprinters are blocked
    driver.get(FINGERPRINTERS_URL)
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("shield-icon").click()
        assert nav.get_element("known-fingerprints").is_displayed()
        # Click on fingerprinters and check if subpanel is correctly displayed
        nav.get_element("known-fingerprints").click()
        assert nav.get_element("fingerprints-blocked-subpanel").is_displayed()
