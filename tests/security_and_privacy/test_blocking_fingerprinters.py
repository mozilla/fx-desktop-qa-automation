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


def test_blocking_fingerprinter(
    driver: Firefox, nav: Navigation, about_prefs_privacy: AboutPrefs
):
    """
    C446404: Blocking Fingerprinters
    """
    # instantiate objects
    about_prefs_privacy.open()

    # Select custom option and keep just known fingerprinters checked
    about_prefs_privacy.select_trackers_to_block("known-fingerprints-checkbox")

    # Access url and click on the shield icon and verify that known fingerprinters are blocked
    driver.get(FINGERPRINTERS_URL)

    nav.open_tracker_panel()
    nav.element_visible("known-fingerprints")

    # Click on fingerprinters and check if subpanel is correctly displayed
    nav.click_on("known-fingerprints")
    nav.element_visible("fingerprints-blocked-subpanel")
