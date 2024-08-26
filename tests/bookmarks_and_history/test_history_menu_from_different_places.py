import platform

from selenium.webdriver import Firefox

from modules.browser_object_menu_bar import MenuBar
from modules.browser_object_panel_ui import PanelUi
from modules.page_object_generics import GenericPage

YOUTUBE_URL = "https://www.youtube.com/"


def test_history_menu_in_different_places(driver: Firefox):
    """
    C118799 - Verify that the History Menu options are displayed from different places (Hamburger Menu, Menu Bar, Toolbar)
    """

    GenericPage(driver, url=YOUTUBE_URL).open()

    # 1. History options from Hamburger Menu
    panel_ui = PanelUi(driver)
    panel_ui.open_history_menu()

    # Check visibility of History elements in the Hamburger Menu
    with driver.context(driver.CONTEXT_CHROME):
        hamburger_menu_elements = {
            "Back Button": "history-back-button",
            "History Title": "history_title",
            "Recently Closed Tabs": "panel-ui-history-recently-closed",
            "Recently Closed Windows": "recently_closed_windows",
            "Search History": "search_history",
            "Clear Recent History": "clear-recent-history",
            "Recent History": "recent_history",
            "Manage History": "manage_history",
        }

        for name, locator in hamburger_menu_elements.items():
            element = panel_ui.get_element(locator)
            assert element.is_displayed(), f"{name} should be visible in Hamburger Menu"

    # 2. History options from Menu Bar
    menu_bar = MenuBar(driver)
    menu_bar.open_menu("History")

    if platform.system() == "Darwin":
        # macOS - Check visibility of History elements using AppleScript
        menu_bar_mac_elements = [
            "Show All History",
            "Clear Recent History…",
            "Restore Previous Session",
            "Search History",
            "Recently Closed Tabs",
            "Recently Closed Windows",
        ]

        for item in menu_bar_mac_elements:
            assert menu_bar.check_menu_item_apple_script(
                "History", item
            ), f"{item} should be visible in the History Menu on macOS"

    else:
        # Windows/Linux - Check visibility of History elements
        with driver.context(driver.CONTEXT_CHROME):
            menu_bar_elements = {
                "Show All History": "menu-bar-show-all-history",
                "Clear Recent History": "menu-bar-clear-recent-history",
                "Restore Previous Session": "menu-bar-restore-previous-session",
                "Search History": "menu-bar-search-history",
                "Recently Closed Tabs": "menu-bar-recently-closed-tabs",
                "Recently Closed Windows": "menu-bar-recently-closed-windows",
            }

            for name, locator in menu_bar_elements.items():
                element = menu_bar.get_element(locator)
                assert element.is_displayed(), f"{name} should be visible in Menu Bar"

    # 3. History options from Toolbar History
    # 4. History options from Toolbar Library
