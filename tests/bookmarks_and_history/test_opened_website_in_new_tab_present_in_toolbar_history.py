import pytest
from selenium.webdriver import Firefox

from modules.browser_object_panel_ui import PanelUi
from modules.browser_object_tabbar import TabBar
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "118802"


FACEBOOK_URL = "https://www.facebook.com/"
AMAZON_URL = "https://www.amazon.com/"
YOUTUBE_URL = "https://www.youtube.com/"

WEBSITES = [FACEBOOK_URL, AMAZON_URL]


def test_the_website_opened_in_new_tab_is_present_in_history_menu(driver: Firefox):
    """
    C118802 - Verify that the website opened in new tab is displayed in the Toolbar History submenu on top of the
    list
    """

    for url in WEBSITES:
        GenericPage(driver, url=url).open()

    tabs = TabBar(driver)

    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    tabs.switch_to_new_tab()

    page = GenericPage(driver, url=YOUTUBE_URL)
    page.open()
    page.url_contains("youtube")

    panel_ui = PanelUi(driver)
    panel_ui.open()
    panel_ui.open_history_menu()

    # Verify YouTube is present in the history menu and is on top of the list as the most recent website visited
    panel_ui.expect_element_attribute_contains(
        "recent-history-content", "value", "YouTube"
    )
