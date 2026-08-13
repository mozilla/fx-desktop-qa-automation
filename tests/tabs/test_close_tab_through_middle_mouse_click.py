import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.page_object import ExamplePage


@pytest.fixture()
def test_case():
    return "134645"


@pytest.mark.headed
def test_close_tab_through_middle_mouse_click(driver: Firefox):
    """
    C134645 - Verify that middle click on a tab will close it
    """
    example = ExamplePage(driver)
    tabs = TabBar(driver)

    # Open 2 new tabs for a total of 3.
    example.open()
    original_handle = driver.current_window_handle
    created_handles = []

    for expected_tab_count in (2, 3):
        handles_before = set(driver.window_handles)

        tabs.new_tab_by_button()
        tabs.wait_for_num_tabs(expected_tab_count)

        new_handles = set(driver.window_handles) - handles_before

        assert len(new_handles) == 1, (
            f"Expected exactly one new tab, but found: {new_handles}"
        )
        created_handles.append(new_handles.pop())

    # Close the third and second tabs using W3C middle-click actions.
    for tab_index, expected_closed_handle in (
        (3, created_handles[1]),
        (2, created_handles[0]),
    ):
        tabs.close_tab_by_middle_click(tab_index)
        tabs.wait_for_num_tabs(tab_index - 1)

        assert expected_closed_handle not in driver.window_handles, (
            f"Expected tab {tab_index} to be closed"
        )
        assert original_handle in driver.window_handles, (
            "Expected the original tab to remain open"
        )
