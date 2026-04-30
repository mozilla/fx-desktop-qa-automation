import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TrustPanel
from modules.page_object import GenericPage
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3054906"


TRACKER_URL = (
    "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting_and_cryptomining_and_cookies.html"
)


def test_trackers_cryptominers_fingerprinters_blocked(
    driver: Firefox, trust_panel: TrustPanel, nav: Navigation
):
    """
    C3054906 - The ETP panel is correctly displayed when the cross-site trackers, cryptominers and fingerprinters are blocked
    """
    # Instantiate objects
    tracker_page = GenericPage(driver, url=TRACKER_URL)
    about_prefs = AboutPrefs(driver, category="privacy")

    # Make sure that the "Standard" option is selected from the ETP section in about:preferences#privacy
    about_prefs.open()
    about_prefs.click_on("standard-radio")

    # wait for the shield icon
    tracker_page.open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    # The Tracking Content is NOT blocked
    trust_panel.trackers_detected("tracking-content")

    # The Cross-Site Tracking Cookies, Fingerpinters and Cryptominers are displayed "Blocked"
    trust_panel.trackers_blocked("tracking-cookies", "cryptominer", "fingerprinter")
