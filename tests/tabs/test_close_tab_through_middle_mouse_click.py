import pytest
from selenium.webdriver import Firefox

from modules.browser_object_tabbar import TabBar
from modules.page_object import ExamplePage


@pytest.fixture()
def test_case():
    return "134645"


@pytest.mark.headed
def test_close_tab_through_middle_mouse_click(driver: Firefox):
    """
    C134645 - Verify that middle click on a tab will close it
    """

    # Instantiate objects
    example = ExamplePage(driver)
    tabs = TabBar(driver)

    # Open 2 new tabs for a total of 3
    example.open()
    for _ in range(2):
        tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(3)

    # Ensure each tab exists and middle-click to close it
    for i in range(3, 1, -1):
        tab_to_close = tabs.get_tab(i)
        assert tab_to_close is not None, f"Expected tab index {i} to exist"
        tabs.middle_click(tab_to_close)
        tabs.wait_for_num_tabs(i - 1)
