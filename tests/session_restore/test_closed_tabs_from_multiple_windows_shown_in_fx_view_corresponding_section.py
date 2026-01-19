import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.page_object_firefox_view import FirefoxView


@pytest.fixture()
def test_case():
    return "2333476"


WINDOW_1_URLS = ["about:about", "about:mozilla", "about:robots"]
WINDOW_2_URLS = ["about:logo", "about:license"]
WINDOW_3_URLS = ["about:buildconfig", "about:credits"]


def close_tabs_from_end(tabs: TabBar, total_tabs: int, count: int) -> None:
    """Close `count` tabs starting from the last tab (by index).

    Arguments:
        tabs: TabBar instance
        total_tabs: Total number of tabs currently open in the window
        count: Number of tabs to close from the end
    """
    for offset in range(count):
        tab_index = total_tabs - offset
        tab = tabs.get_tab(tab_index)
        assert tab is not None, f"Tab not found at index {tab_index}"
        tabs.close_tab(tab)


def assert_recently_closed_contains(
    fx_view: FirefoxView, driver, first_window: str, expected: set[str]
) -> None:
    """Switch to first window, open Firefox View, and verify expected URLs are in Recently Closed."""
    driver.switch_to.window(first_window)
    fx_view.open_recently_closed_section()
    fx_view.wait_for_recently_closed_contains(expected)
    actual = set(fx_view.get_recently_closed_tab_urls())
    assert expected.issubset(actual), f"Expected {expected} not found in {actual}"


def test_fx_view_closed_tabs_from_multiple_windows_shown_in_recently_closed_section(
    driver: Firefox,
):
    """
    C2333476 - Verify that closed tabs from multiple windows are shown in Fx View Recently closed section.
    """
    tabs = TabBar(driver)
    fx_view = FirefoxView(driver)
    first_window = driver.current_window_handle

    # Open web pages in tabs and close the last two
    tabs.open_multiple_tabs_with_pages(WINDOW_1_URLS)
    close_tabs_from_end(tabs, total_tabs=1 + len(WINDOW_1_URLS), count=2)

    # Verify closed tabs are shown in Recently Closed
    assert_recently_closed_contains(
        fx_view, driver, first_window, expected=set(WINDOW_1_URLS[-2:])
    )

    # Open second window with web pages and close them
    tabs.open_and_switch_to_new_window("window")
    tabs_window_2 = TabBar(driver)
    tabs_window_2.open_multiple_tabs_with_pages(WINDOW_2_URLS)
    close_tabs_from_end(
        tabs_window_2, total_tabs=1 + len(WINDOW_2_URLS), count=len(WINDOW_2_URLS)
    )

    # Verify closed tabs from window 2 are shown in Recently Closed
    assert_recently_closed_contains(
        fx_view, driver, first_window, expected=set(WINDOW_2_URLS)
    )

    # Open third window with web pages and close them
    tabs.open_and_switch_to_new_window("window")
    tabs_window_3 = TabBar(driver)
    tabs_window_3.open_multiple_tabs_with_pages(WINDOW_3_URLS)
    close_tabs_from_end(
        tabs_window_3, total_tabs=1 + len(WINDOW_3_URLS), count=len(WINDOW_3_URLS)
    )

    # Verify closed tabs from window 3 are shown in Recently Closed
    assert_recently_closed_contains(
        fx_view, driver, first_window, expected=set(WINDOW_3_URLS)
    )
