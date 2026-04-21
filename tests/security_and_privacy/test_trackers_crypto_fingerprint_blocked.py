import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TrustPanel
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "deprecated"


TRACKER_URL = (
    "https://senglehardt.com/test/trackingprotection/test_pages/"
    "fingerprinting_and_cryptomining_and_cookies.html"
)


def test_cross_site_trackers_crypto_fingerprinter_blocked(
    driver: Firefox, trust_panel: TrustPanel, nav: Navigation
):
    """
    C446393: Ensures that some trackers are blocked on certain website
    """
    # instantiate objs
    tracker_page = GenericPage(driver, url=TRACKER_URL)

    # wait for the shield icon
    tracker_page.open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()
    trust_panel.trackers_detected("tracking-content")
    trust_panel.trackers_blocked("tracking-cookies", "cryptominer")
