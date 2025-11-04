import pytest

from modules.browser_object import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.browser_object_tabbar import TabBar
from modules.page_object_customize_firefox import CustomizeFirefox
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3028770"


def test_searchbar_suggestions_on_engines_remove_restore(driver):
    """
    C3028770 - Verify that removing and restoring search engines reflects search bar suggestions engine.
    """

    # Initialize objects
    nav = Navigation(driver)
    panel_ui = PanelUi(driver)
    customize = CustomizeFirefox(driver)
    tabs = TabBar(driver)
    prefs = AboutPrefs(driver, category="search")

    # Add search bar to toolbar
    panel_ui.open_panel_menu()
    panel_ui.navigate_to_customize_toolbar()
    customize.add_widget_to_toolbar("search-bar")

    # Open about:preferences#search page via Search bar
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    nav.set_search_bar()
    nav.click_on("searchbar-magnifying-glass-button")
    nav.click_on_change_search_settings_button()

    # Remove DuckDuckGo search engine
    prefs.select_search_engine_from_tree("DuckDuckGo")
    prefs.click_on("remove-search-engine button")

    # Open new tab and  verify DuckDuckGo is not in Search bar engine suggestions
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    nav.type_in_search_bar("test")
    nav.element_not_visible("searchbar-search-engine", labels=["DuckDuckGo"])

    # Restore DuckDuckGo search engine
    prefs.open()
    prefs.click_on("restore-default-search-engine button")

    # Open new tab and verify DuckDuckGo is part of the Search bar engine suggestions
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    nav.set_search_bar()
    nav.type_in_search_bar("test")
    nav.element_visible("searchbar-search-engine", labels=["DuckDuckGo"])
