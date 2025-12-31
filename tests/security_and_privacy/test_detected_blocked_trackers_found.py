import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TrackerPanel
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
    driver: Firefox, url: str, tracker_panel: TrackerPanel, nav: Navigation
):
    """
    C446392: Ensure that the correct trackers are allowed and blocked
    """
    generic_page = GenericPage(driver, url=url)

    generic_page.open()
    tracker_panel.wait_for_blocked_tracking_icon(nav, generic_page)
    nav.open_tracker_panel()

    # verify the types of trackers
    tracker_panel.verify_allowed_blocked_trackers(
        {"Tracking Content"}, {"Cross-Site Tracking Cookies"}
    )
