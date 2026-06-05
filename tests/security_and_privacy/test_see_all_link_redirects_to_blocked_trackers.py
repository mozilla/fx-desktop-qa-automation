import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import GenericPage

TEST_URL = "https://edition.cnn.com/"


@pytest.fixture()
def test_case():
    return "3054033"


def test_see_all_link_redirects_to_blocked_trackers(driver: Firefox, trust_panel: TrustPanel):
    """
    C3054033 - “See all” link correctly redirects the user to the blocked trackers
    """

    # Instantiate objects
    test_page = GenericPage(driver, url=TEST_URL)

    # Open test page and click on the shield icon
    test_page.open()
    trust_panel.open_panel()

    # Click on the "See All" button
    trust_panel.click_see_all()

    # The blocked and allowed trackers are displayed in the panel
    trust_panel.element_visible("blocked-items")
    trust_panel.element_visible("detected-items")
