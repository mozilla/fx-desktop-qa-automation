import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import Navigation, PanelUi, TabBar
from modules.page_object import AboutPrefs, CustomizeFirefox


@pytest.fixture()
def test_case():
    return "1365245"


def test_default_search_provider_change_legacy_search_bar(driver: Firefox):
    """
    C1365245 - This test makes sure that the default search
    provider can be changed and settings are applied
    """

    search_term = "what is life?"

    # Create objects
    panel_ui = PanelUi(driver)
    customize_firefox = CustomizeFirefox(driver)
    nav = Navigation(driver)
    tabs = TabBar(driver)
    about_prefs = AboutPrefs(driver, category="search")

    # Open the customize page and add the search bar to the toolbar
    panel_ui.open_panel_menu()
    panel_ui.navigate_to_customize_toolbar()
    customize_firefox.add_widget_to_toolbar("search-bar")

    # Type the search term, click 'Change search settings'
    tabs.new_tab_by_button()
    nav.type_in_search_bar(search_term)
    nav.click_on_change_search_settings_button()

    # Check the current URL is the search settings page
    driver.switch_to.window(driver.window_handles[2])
    assert driver.current_url == "about:preferences#search"

    # Open a site, open search settings again and check if it's opened in a different tab
    driver.get("https://9gag.com/")
    nav.type_in_search_bar(search_term)
    nav.click_on_change_search_settings_button()
    assert driver.current_url == "https://9gag.com/"

    driver.switch_to.window(driver.window_handles[3])
    assert driver.current_url == "about:preferences#search"

    # Set a different provider as a default search engine
    about_prefs.open()
    about_prefs.search_engine_dropdown().select_option("DuckDuckGo")

    # Open the search bar, type the search term and check if the search engine is the one set
    nav.type_in_search_bar(search_term)
    with driver.context(driver.CONTEXT_CHROME):
        search_engine_name_element = driver.find_element(
            By.CSS_SELECTOR, ".searchbar-engine-name"
        )

        assert search_engine_name_element.get_attribute("value") == "DuckDuckGo Search"
