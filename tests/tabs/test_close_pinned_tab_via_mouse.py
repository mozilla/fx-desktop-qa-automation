import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar
from modules.page_object import ExamplePage


@pytest.fixture()
def test_case():
    return "134726"


@pytest.mark.headed
def test_close_pinned_tab_via_middle_click(driver: Firefox):
    """
    C134726 - Verify middle-clicking pinned tab will close it
    """

    example = ExamplePage(driver).open()
    tabs = TabBar(driver)
    tab_menu = ContextMenu(driver)

    # Open 2 new tabs
    for _ in range(2):
        tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(3)

    # Pin the first tab
    with driver.context(driver.CONTEXT_CHROME):
        first_tab = tabs.get_tab(1)
        tabs.context_click(first_tab)
        tab_menu.click_and_hide_menu("context-menu-pin-tab")
        assert tabs.is_pinned(first_tab), "Expected the first tab to be pinned"

        # Middle-click the pinned tab to close it
        tabs.middle_click(first_tab)

    # Verify pinned tab was closed and 2 tabs remain
    tabs.wait_for_num_tabs(2)
