import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import GenericPage

TEST_URL = (
    "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting.html"
)


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

    # Get individual tracker category counts from the detailed view
    cross_site_count = trust_panel.get_cross_site_cookies_count()
    fingerprinter_count = trust_panel.get_fingerprinter_count()

    # Verify the sum of individual categories matches the total shown in the main panel
    assert cross_site_count + fingerprinter_count == total_count, (
        f"Tracker count mismatch: {cross_site_count} cross-site cookies + "
        f"{fingerprinter_count} fingerprinters != {total_count} total"
    )
