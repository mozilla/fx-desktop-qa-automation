import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import Navigation, PanelUi, TabBar
from modules.page_object import AboutPrefs, CustomizeFirefox

SEARCH_TERM = "what is life?"
SEARCH_ENGINE = "DuckDuckGo"
EXPECTED_ENGINE_DISPLAY = "DuckDuckGo Search"
SEARCH_SETTINGS_URL = "about:preferences#search"


@pytest.fixture()
def test_case():
    return "1365245"


def test_default_search_provider_change_legacy_search_bar(driver: Firefox):
    """
    C1365245 - Verify that changing the default search provider is reflected in the legacy search bar.
    """
    panel_ui = PanelUi(driver)
    customize = CustomizeFirefox(driver)
    nav = Navigation(driver)
    tabs = TabBar(driver)
    prefs = AboutPrefs(driver, category="search")

    panel_ui.open_panel_menu()
    panel_ui.navigate_to_customize_toolbar()
    customize.add_widget_to_toolbar("search-bar")

    tabs.new_tab_by_button()
    nav.type_in_search_bar(SEARCH_TERM)
    nav.click_on_change_search_settings_button()
    driver.switch_to.window(driver.window_handles[2])
    assert driver.current_url == SEARCH_SETTINGS_URL

    driver.get("https://9gag.com/")
    nav.type_in_search_bar(SEARCH_TERM)
    nav.click_on_change_search_settings_button()
    assert driver.current_url == "https://9gag.com/"
    driver.switch_to.window(driver.window_handles[3])
    assert driver.current_url == SEARCH_SETTINGS_URL

    prefs.open()
    prefs.search_engine_dropdown().select_option(SEARCH_ENGINE)
    nav.type_in_search_bar(SEARCH_TERM)

    with driver.context(driver.CONTEXT_CHROME):
        engine_name = driver.find_element(By.CSS_SELECTOR, ".searchbar-engine-name")
        assert engine_name.get_attribute("value") == EXPECTED_ENGINE_DISPLAY
