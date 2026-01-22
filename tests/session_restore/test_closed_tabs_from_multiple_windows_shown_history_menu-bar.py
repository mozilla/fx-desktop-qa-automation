import platform

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.browser_object_menu_bar import MenuBar
from modules.page_object_firefox_view import FirefoxView


@pytest.fixture()
def test_case():
    return "2333477"


# URLs for each window
WINDOW_1_URLS = ["about:about", "about:mozilla", "about:robots"]
WINDOW_2_URLS = ["about:buildconfig", "about:credits"]
WINDOW_3_URLS = ["about:license", "about:config"]


@pytest.mark.skipif(
    platform.system() == "Darwin",
    reason="Menu Bar is native on macOS and cannot be accessed.",
)
def test_fx_view_closed_tabs_from_multiple_windows_shown_in_history_menu(
    driver: Firefox,
):
    """
    C2333477 - Verify that closed tabs from multiple windows are shown in History Menu.
    """
    tabs = TabBar(driver)
    fx_view = FirefoxView(driver)
    menu_bar = MenuBar(driver)
    first_window = driver.current_window_handle

    # Window 1 - Open tabs and close the last two
    tabs.open_urls_in_tabs(WINDOW_1_URLS)
    tabs.close_last_n_tabs(total_tabs=1 + len(WINDOW_1_URLS), count=2)

    # Verify closed tabs appear in Firefox View Recently Closed section
    driver.switch_to.window(first_window)
    fx_view.open_recently_closed()
    fx_view.wait_for_closed_tabs_with_urls(set(WINDOW_1_URLS[-2:]))

    # Window 2 - Open new window with tabs
    tabs.open_and_switch_to_new_window("window")
    tabs.clear_cache()
    menu_bar.clear_cache()
    tabs.open_urls_in_tabs(WINDOW_2_URLS)

    # Close tabs and verify in History menu
    tabs.close_last_n_tabs(total_tabs=1 + len(WINDOW_2_URLS), count=len(WINDOW_2_URLS))
    urls = menu_bar.get_recently_closed_urls()
    assert set(WINDOW_2_URLS).issubset(urls), (
        f"Window 2 URLs {WINDOW_2_URLS} not found in {urls}"
    )

    # Window 3 - Open new window with tabs and close them
    driver.switch_to.window(driver.window_handles[-1])
    tabs.open_and_switch_to_new_window("window")
    tabs.clear_cache()
    menu_bar.clear_cache()
    tabs.open_urls_in_tabs(WINDOW_3_URLS)
    tabs.close_last_n_tabs(total_tabs=1 + len(WINDOW_3_URLS), count=len(WINDOW_3_URLS))

    # Verify closed tabs from Window 3 appear in History menu
    urls = menu_bar.get_recently_closed_urls()
    assert set(WINDOW_3_URLS).issubset(urls), (
        f"Window 3 URLs {WINDOW_3_URLS} not found in {urls}"
    )
