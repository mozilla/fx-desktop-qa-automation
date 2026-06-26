import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import GenericPage

TEST_URL = "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting_and_cryptomining_and_cookies.html"


@pytest.fixture()
def test_case():
    return "3054031"


def test_trackers_counted_correctly_in_panel(driver: Firefox, trust_panel: TrustPanel):
    """
    C3054031 - Trackers are correctly counted in the panel
    """

    # Instantiate objects
    test_page = GenericPage(driver, url=TEST_URL)

    # Open test page and click on the shield icon
    test_page.open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    # Get the tracker count from the main panel
    total_count = trust_panel.get_tracker_count()

    # Click See All to open the detailed tracker list
    trust_panel.click_see_all()

    # Sum the per-category counts shown in the detailed view
    blocked_total = trust_panel.get_blocked_trackers_total()

    # Verify the sum of individual categories matches the total shown in the main panel
    assert blocked_total == total_count, (
        f"Tracker count mismatch: detailed categories sum to {blocked_total} "
        f"!= {total_count} total shown in the main panel"
    )
