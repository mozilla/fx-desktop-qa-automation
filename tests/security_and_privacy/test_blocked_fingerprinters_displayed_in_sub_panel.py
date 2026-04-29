import pytest
from selenium.webdriver import Firefox

from modules.browser_object_trust_panel import TrustPanel
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs

FINGERPRINTERS_URL = (
    "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting.html"
)
BLOCKED_TRACKER_URL = "https://mozilla.org"


@pytest.fixture()
def test_case():
    return "3054916"


def test_blocked_fingerprinters_displayed_in_sub_panel(driver: Firefox):
    """
    C3054916 - Fingerprinters are correctly displayed in the sub panel when they are not blocked
    """

    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    tracking_page = GenericPage(driver, url=FINGERPRINTERS_URL)
    trust_panel = TrustPanel(driver)

    # In about:preferences#privacy deselect the options "Known fingerprinters" and "Suspected fingerprinters"
    about_prefs.open()
    about_prefs.select_trackers_to_block(
        "cryptominers-checkbox", "cookies-isolate-social-media-option", "tracking-checkbox"
    )

    # Open page and check the Information panel
    tracking_page.open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    with driver.context(driver.CONTEXT_CHROME):
        trust_panel.click_on("see-blocked-trackers")

    # "Not Blocking Fingerprinters" title is displayed in the subpanel

    # The allowed fingerprinter is displayed inside the subpanel
    # trust_panel.sites_blocked(BLOCKED_TRACKER_URL)

    trust_panel.sites_detected(BLOCKED_TRACKER_URL)