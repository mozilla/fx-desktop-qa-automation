import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TabBar
from modules.page_object import AboutPrefs

TEST_SITE = "https://example.com"
SEARCH_TERM = "what is life?"
SEARCH_ENGINE = "DuckDuckGo"
SEARCH_SETTINGS_URL = "about:preferences#search"


@pytest.fixture()
def test_case():
    return "3028796"


def test_default_search_provider_change_legacy_search_bar(driver: Firefox):
    """
    C1365245 - Verify that changing the default search provider is reflected in
    the legacy search bar.
    """
    nav = Navigation(driver)
    tabs = TabBar(driver)
    prefs = AboutPrefs(driver, category="search")

    # Step 1: Add legacy search bar to toolbar
    nav.add_search_bar_to_toolbar()

    # Step 2: Open a new tab and trigger search settings from search bar
    tabs.new_tab_by_button()
    nav.type_in_search_bar(SEARCH_TERM)
    nav.click_on_legacy_search_settings_button()
    driver.switch_to.window(driver.window_handles[1])
    assert driver.current_url == SEARCH_SETTINGS_URL

    # Step 3: Open site, repeat nav to settings (validates correct tab handling)
    driver.get(TEST_SITE)
    nav.type_in_search_bar(SEARCH_TERM)
    nav.click_on_legacy_search_settings_button()
    nav.url_contains(TEST_SITE)
    driver.switch_to.window(driver.window_handles[2])
    assert driver.current_url == SEARCH_SETTINGS_URL

    # Step 4: Change the default search engine
    prefs.open()
    prefs.select_default_search_engine_by_key(SEARCH_ENGINE)

    # Step 5: Perform another search and validate engine label (via decorated method)
    nav.type_in_search_bar(SEARCH_TERM)
    nav.legacy_search_engine_matches(SEARCH_ENGINE)
