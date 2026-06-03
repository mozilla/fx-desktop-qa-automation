import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import GenericPage

TEST_URL = "https://youtube.com/"


@pytest.fixture()
def test_case():
    return "3054026"


def test_ensure_panel_renders_on_first_run(driver: Firefox):
    """
    C3054026 - The panel opens & renders correctly on the first run
    """

    # Instantiate objects
    test_page = GenericPage(driver, url=TEST_URL)
    trust_panel = TrustPanel(driver)

    # Open test page and click on the shield icon
    test_page.open()
    trust_panel.open_panel()

    # Site icon and its domain are displayed
    trust_panel.element_visible("site-icon")
    trust_panel.element_visible("site-domain")

    # Lock state icon with the text: "Connection secure" are displayed
    trust_panel.element_visible("trustpanel-connect-button")
    trust_panel.element_visible("connection-icon")

    # Purple card
    trust_panel.element_visible("purple-card")

    # “Enhanced Tracking Protection is on” toggle
    trust_panel.element_visible("trustpanel-toggle-button")

    # “Clear cookies and site data”
    trust_panel.element_visible("clear-cookies-button")

    # “Privacy settings”
    trust_panel.element_visible("trustpanel-privacy-link")
