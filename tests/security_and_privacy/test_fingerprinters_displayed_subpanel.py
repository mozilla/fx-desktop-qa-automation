import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import AboutPrefs, GenericPage

FINGERPRINTING_URL = (
    "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting.html"
)
DETECTED_FINGERPRINTER = "https://base-fingerprinting-track-digest256.dummytracker.org"


@pytest.fixture()
def test_case():
    return "3054911"


def test_fingerprinters_displayed_subpanel(driver: Firefox):
    """
    C3054911 - Fingerprinters are correctly displayed in the sub panel
    """

    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    tracking_page = GenericPage(driver, url=FINGERPRINTING_URL)
    trust_panel = TrustPanel(driver)

    # In about:preferences#privacy select only the option "Known fingerprinters" in the Custom section
    about_prefs.open()
    about_prefs.select_trackers_to_block("known-fingerprints-checkbox")

    # Open page and click on the shield icon
    tracking_page.open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    # Click on "See All" button
    trust_panel.click_see_all()

    # Click on Fingerprinters
    trust_panel.open_detected_category("fingerprinter")

    # "Fingerprinters Blocked" title is displayed in the subpanel
    trust_panel.blocked_trackers_title_displayed_in_subpanel("fingerprinters")

    # The blocked fingerprinter is displayed inside the subpanel
    assert trust_panel.has_detected_tracking_sites(DETECTED_FINGERPRINTER)
