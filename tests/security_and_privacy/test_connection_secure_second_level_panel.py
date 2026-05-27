import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import GenericPage

YOUTUBE_URL = "https://youtube.com/"


@pytest.fixture()
def test_case():
    return "3054040"


def test_connection_secure_second_level_panel(driver: Firefox):
    """
    C3054040 - Second level panel for "Connection secure" can be correctly opened
    """

    # Instantiate objects
    test_page = GenericPage(driver, url=YOUTUBE_URL)
    trust_panel = TrustPanel(driver)

    # Open test page and click on the shield icon
    test_page.open()
    trust_panel.open_panel()

    # Click the lock text row (or dedicated “Connection secure” arrow)
    trust_panel.click_connection_button()

    # Second-level panel appears with title “Connection protections for <domain>” text
    trust_panel.element_visible("trustpanel-security-information-view")

    # Click on the back arrow
    trust_panel.click_subview_back_button()

    # The panel returns to main Unified Trust Panel
    trust_panel.element_visible("trustpanel-connection-button")
