import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import GenericPage

MIXED_CONTENT_URL = "https://mixed.badssl.com/"

@pytest.fixture()
def test_case():
    return "3054043"


def test_mixed_content_warning_displayed_in_panel(driver: Firefox):
    """
    C3054043 - Mixed-content warning is correctly displayed inside the panel
    """

    # Instantiate objects
    test_page = GenericPage(driver, url=MIXED_CONTENT_URL)
    trust_panel = TrustPanel(driver)

    # Open test page and click on the shield icon
    test_page.open()
    trust_panel.open_panel()

    # Click the lock text row (or dedicated “Connection secure” arrow)
    trust_panel.click_connection_button()

    # Message shows "You are securely connected to this site"
    trust_panel.connection_secure_message_displayed()

    # "Verified by: Let's Encrypt" message is diplayed inside the panel