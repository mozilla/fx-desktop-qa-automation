import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import GenericPage

HTTP_URL = "http://httpforever.com/"


@pytest.fixture()
def test_case():
    return "3054027"


def test_http_lock_icon_connection_state(driver: Firefox):
    """
    C3054027 - Lock icon and text correctly reflects the connection state (HTTP)
    """

    # Instantiate objects
    test_page = GenericPage(driver, url=HTTP_URL)
    trust_panel = TrustPanel(driver)

    # Open test page and click on the shield icon
    test_page.open()
    trust_panel.open_panel()

    # Top row shows "Connection not secure" text
    trust_panel.element_visible("trustpanel-connection-label-insecure")

    # "Your connection isn't' secure" text is displayed inside the banner
    trust_panel.element_visible("trustpanel-insecure-section-header")
