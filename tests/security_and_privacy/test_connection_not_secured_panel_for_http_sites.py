import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import GenericPage

HTTP_SITE = "http://example.com/"


@pytest.fixture()
def test_case():
    return "3054044"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("dom.security.https_first", False),
        ("dom.security.https_first_pbm", False),
        ("dom.security.https_only_mode", False),
    ]


def test_connection_not_secured_panel_for_http_sites(driver: Firefox):
    """
    C3054044 - Connection not secure is correctly displayed for plain HTTP site
    """

    # Instantiate objects
    test_page = GenericPage(driver, url=HTTP_SITE)
    trust_panel = TrustPanel(driver)

    # Open test page and click on the shield icon
    test_page.open()
    trust_panel.open_panel()

    # Click the lock text row (or dedicated “Connection not secure” arrow)
    trust_panel.click_connection_button()

    # Panel header shows “Connection protections for example.com”
    trust_panel.element_visible("trustpanel-security-information-view")
