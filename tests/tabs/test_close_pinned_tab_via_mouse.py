import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar
from modules.page_object import ExamplePage


@pytest.fixture()
def test_case():
    return "134726"


@pytest.mark.headed
def test_close_pinned_tab_via_mouse(driver: Firefox):
    """
    C134726 - Verify middle-clicking pinned tab will close it
    """
    example = ExamplePage(driver)
    tabs = TabBar(driver)
    tab_menu = ContextMenu(driver)

    # Open 2 new tabs and preserve the handle of the tab to be pinned.
    example.open()
    pinned_tab_handle = driver.current_window_handle

    for _ in range(2):
        tabs.new_tab_by_button()

    tabs.wait_for_num_tabs(3)

    # Pin the first tab and wait for the pinned state.
    tabs.context_click("tab-by-index", labels=["1"])
    tab_menu.click_and_hide_menu("context-menu-pin-tab")
    tabs.element_attribute_is(
        "tab-by-index",
        "pinned",
        "true",
        labels=["1"],
    )

    # Middle-click the freshly located pinned tab.
    tabs.close_tab_by_middle_click(1)

    # Verify that the pinned tab specifically was closed.
    tabs.wait_for_num_tabs(2)
    assert pinned_tab_handle not in driver.window_handles, (
        "Expected the pinned tab to be closed"
    )
