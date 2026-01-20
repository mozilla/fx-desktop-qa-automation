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


def test_fx_view_closed_tabs_from_multiple_windows_shown_in_recently_closed_section(
    driver: Firefox,
):
    """
    C2333476 - Verify that closed tabs from multiple windows are shown in Fx View Recently closed section.
    """
    tabs = TabBar(driver)
    fx_view = FirefoxView(driver)
    first_window = driver.current_window_handle

    # Window 1: Open tabs and close the last two
    tabs.open_urls_in_tabs(WINDOW_1_URLS)
    tabs.close_last_n_tabs(total_tabs=1 + len(WINDOW_1_URLS), count=2)

    # Verify closed tabs appear in Recently Closed
    driver.switch_to.window(first_window)
    fx_view.open_recently_closed()
    fx_view.wait_for_closed_tabs_with_urls(set(WINDOW_1_URLS[-2:]))

    # Window 2: Open new window with tabs and close them
    tabs.open_and_switch_to_new_window("window")
    tabs.clear_cache()
    tabs.open_urls_in_tabs(WINDOW_2_URLS)
    tabs.close_last_n_tabs(total_tabs=1 + len(WINDOW_2_URLS), count=len(WINDOW_2_URLS))

    # Verify closed tabs from window 2 appear in Recently Closed
    driver.switch_to.window(first_window)
    fx_view.open_recently_closed()
    fx_view.wait_for_closed_tabs_with_urls(set(WINDOW_2_URLS))

    # Window 3: Open new window with tabs and close them
    tabs.open_and_switch_to_new_window("window")
    tabs.clear_cache()
    tabs.open_urls_in_tabs(WINDOW_3_URLS)
    tabs.close_last_n_tabs(total_tabs=1 + len(WINDOW_3_URLS), count=len(WINDOW_3_URLS))

    # Verify closed tabs from window 3 appear in Recently Closed
    driver.switch_to.window(first_window)
    fx_view.open_recently_closed()
    fx_view.wait_for_closed_tabs_with_urls(set(WINDOW_3_URLS))
