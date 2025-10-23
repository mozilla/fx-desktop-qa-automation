import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar


@pytest.fixture()
def test_case():
    return "246978"


URLS = [
    "about:about",
    "about:addons",
    "about:cache",
    "about:robots",
]


def test_pin_unpin_selected_tabs(driver: Firefox, sys_platform: str):
    """
    C246978 - Verify that multiple tabs can be selected and pinned/unpinned from the context menu.
    """

    tabs = TabBar(driver)
    # Create 4 new tabs
    for i in range(4):
        tabs.new_tab_by_button()
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(URLS[i])
    assert len(driver.window_handles) == 5

    select_indices = [1, 3, 5]
    selected_tabs = tabs.select_multiple_tabs_by_indices(select_indices, sys_platform)
    tab_context_menu = ContextMenu(driver)

    # Pin
    tab_context_menu.context_click(selected_tabs[1])
    tab_context_menu.click_and_hide_menu(("css selector", "#context_pinSelectedTabs"))

    # Verify pinned
    for tab in selected_tabs:
        assert tabs.is_pinned(tab)

    # Unpin
    tab_context_menu.context_click(selected_tabs[1])
    tab_context_menu.click_and_hide_menu(("css selector", "#context_unpinSelectedTabs"))

    # Verify unpinned
    for tab in selected_tabs:
        assert not tabs.is_pinned(tab)
