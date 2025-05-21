import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi, TabBar
from modules.page_object import AboutPrefs, CustomizeFirefox

SEARCH_TERM = "what is life?"
SEARCH_ENGINE = "DuckDuckGo"
EXPECTED_ENGINE_DISPLAY = "DuckDuckGo Search"
SEARCH_SETTINGS_URL = "about:preferences#search"


@pytest.fixture()
def test_case():
    return "3028796"


def test_default_search_provider_change_legacy_search_bar(driver: Firefox):
    """
    C1365245 - Verify that changing the default search provider is reflected in the legacy search bar.
    """
    nav = Navigation(driver)
    panel_ui = PanelUi(driver)
    customize = CustomizeFirefox(driver)
    tabs = TabBar(driver)
    prefs = AboutPrefs(driver, category="search")

    # Step 1: Add legacy search bar to toolbar
    panel_ui.open_panel_menu()
    panel_ui.navigate_to_customize_toolbar()
    customize.add_widget_to_toolbar("search-bar")

    # Step 2: Open a new tab and trigger search settings from search bar
    tabs.new_tab_by_button()
    nav.type_in_search_bar(SEARCH_TERM)
    nav.click_on_change_search_settings_button()
    driver.switch_to.window(driver.window_handles[2])
    assert driver.current_url == SEARCH_SETTINGS_URL

    # Step 3: Open site, repeat nav to settings (validates correct tab handling)
    driver.get("https://9gag.com/")
    nav.type_in_search_bar(SEARCH_TERM)
    nav.click_on_change_search_settings_button()
    assert driver.current_url == "https://9gag.com/"
    driver.switch_to.window(driver.window_handles[3])
    assert driver.current_url == SEARCH_SETTINGS_URL

    # Step 4: Change the default search engine
    prefs.open()
    prefs.search_engine_dropdown().select_option(SEARCH_ENGINE)

    # Step 5: Perform another search and validate engine label (via decorated method)
    nav.type_in_search_bar(SEARCH_TERM)
    engine_label = nav.get_legacy_search_engine_label()
    assert engine_label == EXPECTED_ENGINE_DISPLAY
