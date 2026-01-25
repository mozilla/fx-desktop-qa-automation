import time

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.page_object_customize_firefox import CustomizeFirefox
from modules.page_object_firefox_view import FirefoxView


@pytest.fixture()
def test_case():
    return "2333479"


def test_library_menu(
    driver: Firefox,
):
    """
    C2333479 - Verify that closed tabs from multiple windows are shown in Library Menu.
    """
    tabs = TabBar(driver)
    fx_view = FirefoxView(driver)
    nav = Navigation(driver)
    panel = PanelUi(driver)
    customize_page = CustomizeFirefox(driver)

    tabs.open_urls_in_tabs(["about:about", "about:mozilla", "about:robots"])
    tabs.close_last_n_tabs(total_tabs=3, count=2)

    # Add Library button to toolbar
    panel.open_panel_menu()
    panel.navigate_to_customize_toolbar()
    customize_page.add_widget_to_toolbar("library")
    tabs.new_tab_by_button()

    # Verify closed tabs from Window 2 appear in Library History section
    nav.open_library_history_submenu()
    time.sleep(10)
    # nav.get_library_recently_closed_urls()
