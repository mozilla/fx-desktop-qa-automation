import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import AboutPrefs, GenericPage

FINGERPRINTERS_URL = (
    "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting.html"
)


@pytest.fixture()
def test_case():
    return "387363"


def test_fingerprinters_blocked_and_shown_in_panel_and_preferences(driver: Firefox):
    """
    C387363 - Fingerprinters are blocked and shown correctly (Control Center and Preferences)
    """

    # Instantiate objects
    tracking_page = GenericPage(driver, url=FINGERPRINTERS_URL)
    trust_panel = TrustPanel(driver)
    about_prefs = AboutPrefs(driver, category="privacy")

    # Open page and check the Information panel
    tracking_page.open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    # The "Blocked" string is displayed under the Fingerprinters section
    trust_panel.trackers_blocked("fingerprinter")

    # Navigate to about:preferences#privacy
    about_prefs.open()

    # Check Standard section
    about_prefs.click_on("standard-radio")

    # Check Standard section contains "Fingerprinters"
    standard_section = about_prefs.get_element("standard-section")
    assert "Fingerprinters" in standard_section.text
