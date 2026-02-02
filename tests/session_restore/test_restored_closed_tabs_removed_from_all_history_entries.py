import platform

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.browser_object_panel_ui import PanelUi
from modules.page_object_firefox_view import FirefoxView


@pytest.fixture()
def test_case():
    return "2333482"


URLS_TO_CLOSE = {
    "window1": ["about:mozilla", "about:robots"],
    "window2": ["about:logo", "about:license"],
    "window3": ["about:buildconfig", "about:credits"],
}
ALL_CLOSED_URLS = set(sum(URLS_TO_CLOSE.values(), []))


def test_restored_closed_tabs_removed_from_all_history_entries(driver: Firefox):
    """
    C2333482 - Verify that closed tabs from multiple windows can be restored via Hamburger Menu > History > Recently
    Closed Tabs > Reopen All Tabs, and that they are removed from Firefox View, hamburger menu, and History menu bar.
    """
    # Initialize objects
    tabs = TabBar(driver)
    fx_view = FirefoxView(driver)
    panel = PanelUi(driver)
    main_window = driver.current_window_handle

    # Helper method to open tabs in a new window and close them
    def close_tabs_in_new_window(urls: list[str]):
        """Open a new window, create tabs for URLs, then close them."""
        driver.switch_to.window(main_window)
        tabs.open_and_switch_to_new_window("window")
        tabs.clear_cache()
        tabs.open_urls_in_tabs(urls)
        tabs.close_last_n_tabs(total_tabs=1 + len(urls), count=len(urls))

    # Close tabs across multiple windows
    tabs.open_urls_in_tabs(["about:about"] + URLS_TO_CLOSE["window1"])
    tabs.close_last_n_tabs(total_tabs=4, count=2)  # leave one tab opened

    close_tabs_in_new_window(URLS_TO_CLOSE["window2"])
    close_tabs_in_new_window(URLS_TO_CLOSE["window3"])

    # Verify closed tabs appear in Firefox View
    driver.switch_to.window(main_window)
    fx_view.open_recently_closed()
    fx_view.wait_for_closed_tabs_with_urls(ALL_CLOSED_URLS)

    # Restore all closed tabs via Panel UI (must navigate away from Firefox View first)
    tabs.open()
    panel.clear_cache()
    panel.reopen_all_recently_closed_tabs()
    tabs.custom_wait(timeout=30).until(
        lambda _: ALL_CLOSED_URLS.issubset(tabs.get_all_window_urls())
    )

    # Verify all recently closed lists are now empty
    # Verify Firefox View
    driver.switch_to.window(main_window)
    fx_view.clear_cache()
    fx_view.open_recently_closed()
    fx_view.wait_for_no_closed_tabs()

    # Verify Panel UI
    panel.verify_urls_not_in_recently_closed(ALL_CLOSED_URLS)

    # Verify Menu Bar (not on macOS)
    if platform.system() != "Darwin":
        from modules.browser_object_menu_bar import MenuBar

        menu_bar = MenuBar(driver)
        assert len(menu_bar.get_recently_closed_urls()) == 0, (
            "Expected no recently closed tabs in menu bar"
        )
