import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation, PanelUi, TabBar
from modules.page_object import AboutPrefs, CustomizeFirefox
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "3028778"


SEARCH_TERM = "mozilla"
SEARCH_ENGINE = "DuckDuckGo"
RANDOM_URL = "https://www.example.com"


def test_search_bar_results_shown_in_a_new_tab(driver: Firefox):
    """
    C3028778 - Verify that searches from search bar open results in a new tab.
    """
    # Instantiate objects
    nav = Navigation(driver)
    panel_ui = PanelUi(driver)
    customize = CustomizeFirefox(driver)
    tabs = TabBar(driver)
    prefs = AboutPrefs(driver, category="search")
    page = GenericPage(driver, url=RANDOM_URL)

    # Set DuckDuckGo as default search engine
    prefs.open()
    prefs.search_engine_dropdown().select_option(SEARCH_ENGINE)

    # Add Search Bar to toolbar
    tabs.new_tab_by_button()
    panel_ui.open_panel_menu()
    panel_ui.navigate_to_customize_toolbar()
    customize.add_widget_to_toolbar("search-bar")

    # Open a random link in a new tab
    tabs.new_tab_by_button()
    page.open()

    # Perform a search from search bar and verify ALT+ENTER displays results in a new tab
    nav.type_in_search_bar(SEARCH_TERM)
    nav.perform_key_combo_chrome(Keys.ALT, Keys.ENTER)
    tabs.switch_to_new_tab()
    nav.url_contains(SEARCH_TERM)
