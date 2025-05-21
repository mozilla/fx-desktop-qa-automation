import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import AboutPrefs

WAIT_TIMEOUT = 10
SEARCH_ENGINE = "DuckDuckGo"
EXPECTED_PLACEHOLDER = f"Search with {SEARCH_ENGINE} or enter address"


@pytest.fixture()
def test_case():
    return "3028795"


@pytest.mark.ci
def test_default_search_provider_change_awesome_bar(driver: Firefox):
    """
    C2860208 - Verify that changing the default search provider updates the address bar placeholder.
    """
    nav = Navigation(driver)
    prefs = AboutPrefs(driver)

    # Step 1: Open new tab and go to search engine settings
    driver.get("about:newtab")
    nav.open_searchmode_switcher_settings()

    # Step 2: Change the default search engine
    prefs.search_engine_dropdown().select_option(SEARCH_ENGINE)

    # Step 3: Re-open new tab and verify placeholder
    driver.get("about:newtab")
    nav.expect_element_attribute_contains("awesome-bar", "placeholder", EXPECTED_PLACEHOLDER)
