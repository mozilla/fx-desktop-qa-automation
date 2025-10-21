from time import sleep

import pytest
from selenium.webdriver import Firefox, Keys
from selenium.webdriver.common.by import By

from modules.browser_object_navigation import Navigation
from modules.page_object_prefs import AboutPrefs

TEST_URL = "https://addons.mozilla.org/en-US/firefox"
SEARCH_ENGINE = "Bugzilla@Mozilla"
TEXT = "test"


@pytest.fixture()
def test_case():
    return "3028769"


@pytest.mark.parametrize("engine", ["bugzilla@mozilla"])
def test_added_open_search_engine_default(driver: Firefox, engine):
    """
    C3028769 - Added Open Search Engine can be made default search engine
    """

    # Instantiate objects
    nav = Navigation(driver)
    prefs = AboutPrefs(driver, category="search")

    # Open website that has autodiscovery
    driver.get(TEST_URL)

    # Click in the address bar and delete/add a letter in the URL to enter the edit mode
    nav.type_in_awesome_bar(TEXT)

    # Open the Unified Search button and click on the option to add the search engine : "Add + name_of_search_engine"
    with driver.context(driver.CONTEXT_CHROME):
        nav.click_search_mode_switcher()
        # nav.set_search_mode(engine)
        element = driver.find_element(By.CSS_SELECTOR, "menuitem.menuitem-iconic.searchmode-switcher-installed[label='Firefox Add-ons']")

        element.click()

    # Open in a new tab about:preferences#search
    prefs.open()

    # Set the newly added engine as a default engine.
    prefs.search_engine_dropdown().select_option(SEARCH_ENGINE)

    # Open a new tab and in the address bar type a search string and press enter





