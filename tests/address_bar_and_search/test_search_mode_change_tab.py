import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar

TEXT = "Fire"
SERP_URLS = {"Bing": "bing.com", "DuckDuckGo": "duckduckgo.com"}


@pytest.fixture()
def test_case():
    return "3028732"


@pytest.mark.parametrize("engine1, engine2", [("Bing", "DuckDuckGo")])
def test_search_mode_change_tab(driver: Firefox, engine1, engine2):
    """
    C3028732 - Verify that searchmode with change tab works correctly
    """

    # Instantiate objects
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Click on Bing engine
    first_tab = driver.current_window_handle
    nav.set_search_mode(engine1)

    # "Search Mode" is visible in URL bar for Bing
    nav.verify_search_mode_is_visible(engine1)

    # Open a new tab and click on the USB
    nav.open_and_switch_to_new_window("tab")
    second_tab = driver.current_window_handle

    # Click on the Duckduckgo engine
    nav.set_search_mode(engine2)

    # "Search Mode" is visible in URL bar for duckduckgo
    nav.verify_search_mode_is_visible(engine2)

    # Go back to tab from step #2, "Search Mode" appears as Bing
    tabs.click_tab_by_index(1)
    driver.switch_to.window(first_tab)
    nav.verify_search_mode_is_visible(engine1)

    # Type any word and hit enter, search is done using Bing engine
    nav.search(TEXT)
    nav.url_contains(SERP_URLS[engine1])

    # Go back to the tab from step #4, "Search Mode" appears as DuckDuckGo
    tabs.click_tab_by_index(2)
    driver.switch_to.window(second_tab)
    nav.verify_search_mode_is_visible(engine2)

    # Type any word and hit enter, search is done using the duckduckgo engine
    nav.search(TEXT)
    nav.url_contains(SERP_URLS[engine2])
