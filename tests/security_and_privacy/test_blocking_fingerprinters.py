import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.browser_object_trust_panel import TrustPanel
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3054911"


FINGERPRINTERS_URL = (
    "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting.html"
)


def test_blocking_fingerprinter(
    driver: Firefox,
    nav: Navigation,
    about_prefs_privacy: AboutPrefs,
    trust_panel: TrustPanel,
    tabs: TabBar,
):
    """
    C446404: Blocking Fingerprinters
    """
    # Instantiate objects
    about_prefs_privacy.open()
    tracking_page = GenericPage(driver, url=FINGERPRINTERS_URL)

    # Select custom option and keep just known fingerprinters checked
    about_prefs_privacy.select_trackers_to_block("known-fingerprints-checkbox")

    tracking_page.open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    # Open the tracker panel and verify fingerprinters are visible
    trust_panel.trackers_blocked("fingerprinter")
