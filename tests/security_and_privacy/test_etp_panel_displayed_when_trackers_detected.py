import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import GenericPage

TEST_URL = "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting_and_cryptomining_and_cookies.html"


@pytest.fixture()
def test_case():
    return "3054905"


def test_etp_panel_displayed_when_trackers_detected(driver: Firefox, trust_panel: TrustPanel):
    """
    C3054905 - The ETP panel is correctly displayed when the blocked trackers are detected
    """

    # Instantiate objects
    test_page = GenericPage(driver, url=TEST_URL)

    # Open test page and click on the shield icon
    test_page.open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    # Click on the "See All" button
    trust_panel.click_see_all()

    # The trackers blocked on the page are listed under the section "Firefox blocked these things for you:"
    # which includes: "x Cross-site tracking cookies", "x Fingerprinters" and "x Cryptominer"
    trust_panel.detected_category_visible("cryptominer")
    trust_panel.detected_category_visible("fingerprinter")
    trust_panel.detected_category_visible("tracking cookies")

