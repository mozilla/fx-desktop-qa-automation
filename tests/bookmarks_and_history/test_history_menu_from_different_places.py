from selenium.webdriver import Firefox

from modules.browser_object_menu_bar import MenuBar
from modules.browser_object_panel_ui import PanelUi
from modules.page_object_generics import GenericPage

YOUTUBE_URL = "https://www.youtube.com/"


def test_history_menu_in_different_places(driver: Firefox):
    """
    C118799 - Verify that the History Menu options are displayed from different places (Hamburger Menu, Menu Bar,
    Toolbar)
    """

    GenericPage(driver, url=YOUTUBE_URL).open()

    # History options from Hamburger Menu
    panel_ui = PanelUi(driver)
    panel_ui.open_history_menu()

    # Locate all the elements from the History submenu
    with driver.context(driver.CONTEXT_CHROME):
        hm_back_button = panel_ui.get_element("history-back-button")
        hm_history_title = panel_ui.get_element("history_title")
        hm_recently_closed_tabs = panel_ui.get_element(
            "panel-ui-history-recently-closed"
        )
        hm_recently_closed_windows = panel_ui.get_element("recently_closed_windows")
        hm_search_history = panel_ui.get_element("search_history")
        hm_clear_recent_history = panel_ui.get_element("clear-recent-history")
        hm_recent_history = panel_ui.get_element("recent_history")
        hm_manage_history = panel_ui.get_element("manage_history")

        # Check that all the elements from the History submenu are visible to the user
        assert hm_back_button.is_displayed()
        assert hm_history_title.is_displayed()
        assert hm_recently_closed_tabs.is_displayed()
        assert hm_recently_closed_windows.is_displayed()
        assert hm_search_history.is_displayed()
        assert hm_clear_recent_history.is_displayed()
        assert hm_recent_history.is_displayed()
        assert hm_manage_history.is_displayed()

    # History options from  Menu Bar
    menu_bar = MenuBar(driver)
    menu_bar.open_history_menu()

    # Locate all the elements from the History submenu
    with driver.context(driver.CONTEXT_CHROME):
        mb_show_all_history = menu_bar.get_element("menu-bar-show-all-history")
        mb_clear_recent_history = menu_bar.get_element("menu-bar-clear-recent-history")
        mb_restore_previous_session = menu_bar.get_element(
            "menu-bar-restore-previous-session"
        )
        mb_search_history = menu_bar.get_element("menu-bar-search-history")
        mb_recently_closed_tabs = menu_bar.get_element("menu-bar-recently-closed-tabs")
        mb_recently_closed_windows = menu_bar.get_element(
            "menu-bar-recently-closed-windows"
        )

        # Check that all the elements from the History submenu are visible to the user
        assert mb_show_all_history.is_displayed()
        assert mb_clear_recent_history.is_displayed()
        assert mb_restore_previous_session.is_displayed()
        assert mb_search_history.is_displayed()
        assert mb_recently_closed_tabs.is_displayed()
        assert mb_recently_closed_windows.is_displayed()

    # History options from  Toolbar
    # TBD
