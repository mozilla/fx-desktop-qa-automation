import platform

from selenium.webdriver import Firefox

from modules.browser_object_menu_bar import MenuBar
from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.browser_object_tabbar import TabBar
from modules.browser_object_toolbar import Toolbar
from modules.page_object_customize_firefox import CustomizeFirefox


def assert_elements_visibility(ui_object, elements: dict, source: str):
    """Helper function to assert visibility of elements in a given UI source."""
    for name, locator in elements.items():
        element = ui_object.get_element(locator)
        assert element.is_displayed(), f"{name} should be visible in {source}"


def test_history_menu_in_different_places(driver: Firefox):
    """
    C118799 - Verify that the History Menu options are displayed from different places (Hamburger Menu, Menu Bar,
    Toolbar)
    """

    # 1. History options from Hamburger Menu
    panel_ui = PanelUi(driver)
    panel_ui.open_history_menu()

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
        assert_elements_visibility(panel_ui, hamburger_menu_elements, "Hamburger Menu")

    # 2. History options from Menu Bar
    menu_bar = MenuBar(driver)

    if platform.system() != "Darwin":
        menu_bar.open_menu("History")

        with driver.context(driver.CONTEXT_CHROME):
            menu_bar_elements = {
                "Show All History": "menu-bar-show-all-history",
                "Clear Recent History": "menu-bar-clear-recent-history",
                "Restore Previous Session": "menu-bar-restore-previous-session",
                "Search History": "menu-bar-search-history",
                "Recently Closed Tabs": "menu-bar-recently-closed-tabs",
                "Recently Closed Windows": "menu-bar-recently-closed-windows",
            }
            assert_elements_visibility(menu_bar, menu_bar_elements, "Menu Bar")
    else:
        print("Skipping Menu Bar verification on macOS")

    # 3. History options from Toolbar (History and Library)
    customize_firefox = CustomizeFirefox(driver)
    tabs = TabBar(driver).open()
    nav = Navigation(driver)
    toolbar = Toolbar(driver)

    panel_ui.navigate_to_customize_toolbar()
    customize_firefox.add_widget_to_toolbar("history")
    customize_firefox.add_widget_to_toolbar("library")

    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()

    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("history-button").click()

        history_toolbar_elements = {
            "Recently Closed Tabs": "toolbar-history-recently-closed-tabs",
            "Recently Closed Windows": "toolbar-history-recently-closed-windows",
            "Search History": "toolbar-history-search-history",
            "Clear Recent History": "toolbar-history-clear-recent-history",
            "Recent History": "toolbar-history-recent_history",
            "Manage History": "toolbar-history-manage_history",
        }
        assert_elements_visibility(toolbar, history_toolbar_elements, "Toolbar History")

        nav.get_element("library-button").click()
        nav.get_element("library-history-submenu-button").click()

        library_toolbar_elements = (
            history_toolbar_elements  # Reuse the same locators from a different path
        )
        assert_elements_visibility(toolbar, library_toolbar_elements, "Toolbar Library")
