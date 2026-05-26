import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.browser_object_trust_panel import TrustPanel
from modules.page_object_generics import GenericPage

YOUTUBE_URL = "https://www.youtube.com"
PREFERENCES_URL = "about:preferences#privacy"


@pytest.fixture()
def test_case():
    return "3054036"


def test_privacy_settings_footer_link_opens_correct_page(driver: Firefox):
    """
    C3054036 - “Privacy settings” footer link opens the correct page
    """

    # Instantiate objects
    test_page = GenericPage(driver, url=YOUTUBE_URL)
    trust_panel = TrustPanel(driver)
    tabs = TabBar(driver)
    nav = Navigation(driver)

    # Open test page and click on the shield icon
    test_page.open()
    trust_panel.open_panel()

    # Click on the “Privacy settings” footer link
    trust_panel.click_privacy_settings_link()

    # "about:preferences#privacy" is opened in a new tab
    tabs.switch_to_new_tab()
    nav.url_contains(PREFERENCES_URL)
