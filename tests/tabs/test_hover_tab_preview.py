import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar

NUM_TABS = 10
PINNED_TABS = 3


@pytest.fixture()
def test_case():
    return "2693897"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.tabs.hoverPreview.enabled", True)]


def test_hover_tab_preview(driver: Firefox):
    # Instantiate objects
    tabs = TabBar(driver)
    tab_context_menu = ContextMenu(driver)

    # Opening some tabs
    for _ in range(NUM_TABS):
        tabs.new_tab_by_button()

    # Pin the first few tabs
    for i in range(1, PINNED_TABS + 1):
        tab = tabs.get_tab(i)
        tabs.context_click(tab)
        tab_context_menu.click_and_hide_menu("context-menu-pin-tab")
