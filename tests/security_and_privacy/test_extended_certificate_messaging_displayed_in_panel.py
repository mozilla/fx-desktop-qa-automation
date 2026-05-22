import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import GenericPage

EXTENDED_CERTIFICATE_URL = "https://extended-validation.badssl.com/"

@pytest.fixture()
def test_case():
    return "3054042"


def test_extended_certificate_messaging_displayed_in_panel(driver: Firefox):
    """
    C3054042 - Extended Certificate messaging is correctly displayed inside the panel
    """

    # Instantiate objects
    test_page = GenericPage(driver, url=EXTENDED_CERTIFICATE_URL)
    trust_panel = TrustPanel(driver)

    # Open test page and click on the shield icon
    test_page.open()
    trust_panel.open_panel()

    # Click the lock text row (or dedicated “Connection secure” arrow)
    trust_panel.click_connection_button()

    # Message shows "You are not securely connected to this site"
    trust_panel.connection_not_secure_message_displayed()
