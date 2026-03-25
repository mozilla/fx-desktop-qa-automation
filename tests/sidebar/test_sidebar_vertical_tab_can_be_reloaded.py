import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, TabBar

URL = "about:robots"


@pytest.fixture()
def test_case():
    return "2652386"


def test_sidebar_vertical_tab_can_be_reloaded(driver: Firefox):
    """
    C2652386 - Verify that a vertical tab can be reloaded via the context menu in the sidebar.
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)

    nav.toggle_vertical_tabs()
    driver.get(URL)
    nav.url_contains("robots")

    tab_title = tabs.get_tab_title(tabs.get_tab(1))

    tabs.context_click(tabs.get_tab(1))
    context_menu.click_and_hide_menu("context-menu_reload-tab")

    # url title is stable across reload, the action is completed without errors
    tabs.wait_for_tab_title(tab_title, tab_index=1)
