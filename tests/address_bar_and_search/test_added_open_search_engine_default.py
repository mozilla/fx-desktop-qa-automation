from time import sleep

import pytest
from selenium.webdriver import Firefox, Keys
from selenium.webdriver.common.by import By

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_prefs import AboutPrefs

TEST_URL = "https://addons.mozilla.org/en-US/firefox"
SEARCH_ENGINE = "Firefox Add-ons"
TEXT = "test"
TEST_TEXT = "Firefox"
EXPECTED_URL = "https://addons.mozilla.org/en-US/firefox/search/?q=Firefox"


@pytest.fixture()
def test_case():
    return "3028769"


@pytest.mark.parametrize("engine", ["Firefox Add-ons"])
def test_added_open_search_engine_default(driver: Firefox, engine):
    """
    C3028769 - Added Open Search Engine can be made default search engine
    """

    # Instantiate objects
    nav = Navigation(driver)
    prefs = AboutPrefs(driver, category="search")
    tabs = TabBar(driver)

    # Open website that has autodiscovery
    driver.get(TEST_URL)

    # Click in the address bar and delete/add a letter in the URL to enter the edit mode
    nav.type_in_awesome_bar(TEXT)

    # Open the Unified Search button and click on the option to add the search engine : "Add + name_of_search_engine"
    nav.click_search_mode_switcher()
    nav.set_search_mode(engine)

    # Open in a new tab about:preferences#search
    prefs.open()

    # Set the newly added engine as a default engine.
    prefs.search_engine_dropdown().select_option(SEARCH_ENGINE)

    # Open a new tab and in the address bar type a search string and press enter
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    nav.type_in_awesome_bar(TEST_TEXT + Keys.ENTER)

    # Check that search is performed with the newly added default engine and search results are displayed
    assert nav.url_contains(EXPECTED_URL)
