import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TrustPanel
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "446392"


urls = [
    "https://www.bbc.com/",
    "https://senglehardt.com/test/trackingprotection/test_pages/tracking_protection",
]


@pytest.mark.parametrize("url", urls)
def test_detected_blocked_trackers_found(
    driver: Firefox, url: str, trust_panel: TrustPanel, nav: Navigation
):
    """
    C446392: Ensure that the correct trackers are allowed and blocked
    """
    generic_page = GenericPage(driver)

    generic_page.driver.get(url)
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    # verify the types of trackers
    trust_panel.trackers_detected("tracking-content")
    trust_panel.trackers_blocked("tracking-cookies")
