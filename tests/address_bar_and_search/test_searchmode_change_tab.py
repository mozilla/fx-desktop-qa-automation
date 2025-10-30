import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar

TEXT = "Fire"


@pytest.fixture()
def test_case():
    return "3028732"


@pytest.mark.parametrize("engine1, engine2", [("Bing", "DuckDuckGo")])
def test_searchmode_change_tab(driver: Firefox, engine1, engine2):
    """
    C3028732 - Verify that searchmode with change tab works correctly
    """

    # Instantiate objects
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Click on the USB
    nav.click_search_mode_switcher()

    # Click on Bing engine
    nav.set_search_mode(engine1)

    # "Search Mode" is visible in URL bar for Bing
    nav.verify_engine_returned(engine1)

    # Open a new tab and click on the USB
    nav.open_and_switch_to_new_window("tab")
    nav.click_search_mode_switcher()

    # Click on the Duckduckgo engine
    nav.set_search_mode(engine2)

    # "Search Mode" is visible in URL bar for duckduckgo
    nav.verify_engine_returned(engine2)

    # Go back to tab from step #2
    tabs.click_tab_by_index(1)

    # Type any word and hit enter
    nav.search(TEXT)

    # Check search is done using Bing engine
    nav.verify_engine_returned(engine1)

    # Go back to the tab from step #4
    tabs.click_tab_by_index(2)

    # Type any word and hit enter
    nav.search(TEXT)

    # Check that search is done using the duckduckgo engine
    nav.verify_engine_returned(engine2)
