import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import GenericPage

YOUTUBE_URL = "https://youtube.com/"


@pytest.fixture()
def test_case():
    return "3054041"


def test_secure_domain_certificate_messaging_panel(driver: Firefox):
    """
    C3054041 - Secure Domain Validate certificate messaging is correctly displayed in the panel
    """

    # Instantiate objects
    test_page = GenericPage(driver, url=YOUTUBE_URL)
    trust_panel = TrustPanel(driver)

    # Open test page and click on the shield icon
    test_page.open()
    trust_panel.open_panel()

    # Click the lock text row (or dedicated “Connection secure” arrow)
    trust_panel.click_connection_button()

    # The text is displayed: “You are securely connected to this site”
    trust_panel.connection_secure_message_displayed()
