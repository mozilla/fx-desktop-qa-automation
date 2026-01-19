import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.page_object_firefox_view import FirefoxView


@pytest.fixture()
def test_case():
    return "2333476"


WINDOW_1_URLS = [
    "about:about",
    "about:mozilla",
    "about:robots",
]

WINDOW_2_URLS = [
    "about:logo",
    "about:license",
]

WINDOW_3_URLS = [
    "about:buildconfig",
    "about:credits",
]


def test_fx_view_closed_tabs_from_multiple_windows_shown_in_recently_closed_section(
    driver: Firefox,
):
    """
    C2333476 - Verify that closed tabs from multiple windows are shown in Fx View Recently closed section.
    """
    tabs = TabBar(driver)
    fx_view = FirefoxView(driver)
    first_window = driver.current_window_handle

    # Open a few random web pages in different tabs
    tabs.open_multiple_tabs_with_pages(WINDOW_1_URLS)

    # Close the last two tabs
    num_tabs = len(driver.window_handles)
    for i in range(2):
        tab = tabs.get_tab(num_tabs - i)
        assert tab is not None
        tabs.close_tab(tab)

    # Switch to the first window handle
    driver.switch_to.window(first_window)

    # Navigate to Firefox View Recently Closed section
    fx_view.open_recently_closed_section()

    # Verify that closed tabs are shown in Recently Closed section
    expected_closed_urls = set(WINDOW_1_URLS[-2:])
    fx_view.wait.until(
        lambda _: set(fx_view.get_recently_closed_tab_urls()) == expected_closed_urls
    )
    actual_closed_urls = set(fx_view.get_recently_closed_tab_urls())
    assert actual_closed_urls == expected_closed_urls

    # Open another Firefox window with some random web pages in different tabs
    tabs.open_and_switch_to_new_window("window")
    tabs_window_2 = TabBar(driver)
    tabs_window_2.open_multiple_tabs_with_pages(WINDOW_2_URLS)

    # Close some tabs in the new Firefox window and navigate to Firefox View in the first window
    num_tabs_window_2 = len(WINDOW_2_URLS) + 1  # +1 for the initial blank tab
    for i in range(len(WINDOW_2_URLS)):
        tab = tabs_window_2.get_tab(num_tabs_window_2 - i)
        tabs_window_2.close_tab(tab)

    # Switch to first window and navigate to Firefox View
    driver.switch_to.window(first_window)
    fx_view.open_recently_closed_section()

    # Verify closed tabs from the new Firefox window are shown in Recently Closed
    expected_window_2_urls = set(WINDOW_2_URLS)
    fx_view.wait.until(
        lambda _: expected_window_2_urls.issubset(
            set(fx_view.get_recently_closed_tab_urls())
        )
    )
    actual_closed_urls = set(fx_view.get_recently_closed_tab_urls())
    assert expected_window_2_urls.issubset(actual_closed_urls)

    # Open another Firefox window with some random web pages and close those tabs
    tabs.open_and_switch_to_new_window("window")
    tabs_window_3 = TabBar(driver)
    tabs_window_3.open_multiple_tabs_with_pages(WINDOW_3_URLS)

    # Close the tabs in window 3
    num_tabs_window_3 = len(WINDOW_3_URLS) + 1
    for i in range(len(WINDOW_3_URLS)):
        tab = tabs_window_3.get_tab(num_tabs_window_3 - i)
        tabs_window_3.close_tab(tab)

    # Switch to first window and navigate to Firefox View
    driver.switch_to.window(first_window)
    fx_view.open_recently_closed_section()

    # Verify closed tabs from the third Firefox window are shown in Recently Closed
    expected_window_3_urls = set(WINDOW_3_URLS)
    fx_view.wait.until(
        lambda _: expected_window_3_urls.issubset(
            set(fx_view.get_recently_closed_tab_urls())
        )
    )
    actual_closed_urls = set(fx_view.get_recently_closed_tab_urls())
    assert expected_window_3_urls.issubset(actual_closed_urls)
