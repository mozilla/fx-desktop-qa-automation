import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_prefs import AboutPrefs

"""Force rerun"""


@pytest.fixture()
def test_case():
    return "446404"


FINGERPRINTERS_URL = (
    "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting.html"
)


def test_blocking_fingerprinter(driver: Firefox):
    """
    C446404: Blocking Fingerprinters
    """
    # instantiate objects
    nav = Navigation(driver)
    about_prefs = AboutPrefs(driver, category="privacy")
    about_prefs.open()

    # Select custom option and keep just known fingerprinters checked
    about_prefs.get_element("custom-radio").click()
    about_prefs.get_element("cookies-checkbox").click()
    about_prefs.get_element("tracking-checkbox").click()
    about_prefs.get_element("cryptominers-checkbox").click()
    about_prefs.get_element("suspected-fingerprints-checkbox").click()

    # Access url and click on the shield icon and verify that known fingerprinters are blocked
    driver.get(FINGERPRINTERS_URL)
    nav.click_on("shield-icon")
    nav.element_visible("known-fingerprints")

    # Click on fingerprinters and check if subpanel is correctly displayed
    nav.click_on("known-fingerprints")
    nav.element_visible("fingerprints-blocked-subpanel")
