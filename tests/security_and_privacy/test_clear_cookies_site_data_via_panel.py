import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import GenericPage

TEST_URL = "https://youtube.com/"


@pytest.fixture()
def test_case():
    return "3054035"


def test_clear_cookies_site_data_via_panel(driver: Firefox):
    """
    C3054035 - “Clear cookies and site data” action works as expected
    """

    # Instantiate objects
    test_page = GenericPage(driver, url=TEST_URL)
    trust_panel = TrustPanel(driver)

    # Open test page and click on the shield icon
    test_page.open()
    trust_panel.open_panel()

    # Click on the "Clear cookies and site data" option -> Clear
    trust_panel.clear_cookies_site_date_via_panel()

    # "Clear cookies and site data" dialog is dismissed
    trust_panel.panel_is_dismissed()
