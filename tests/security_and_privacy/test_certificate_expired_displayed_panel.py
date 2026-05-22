import pytest
from selenium.webdriver import Firefox

from modules.browser_object_trust_panel import TrustPanel
from modules.page_object_generics import GenericPage

CERTIFICATE_EXPIRED_URL = "https://expired.badssl.com/"


@pytest.fixture()
def test_case():
    return "3054045"


def test_certificate_expired_displayed_panel(driver: Firefox):
    """
    C3054045 - “Certificate expired” is correctly displayed in the panel
    """

    # Instantiate objects
    test_page = GenericPage(driver, url=CERTIFICATE_EXPIRED_URL)
    trust_panel = TrustPanel(driver)

    # Open test page and click on the shield icon
    test_page.open()
    trust_panel.open_panel()

    # Click the lock text row (or dedicated “Connection not secure” arrow)
    trust_panel.click_connection_button()

    # The panel displays red error text: "You are not securely connected to this site"
    trust_panel.connection_not_secure_message_displayed()
