import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import Navigation
from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "2860208"


@pytest.mark.ci
@pytest.mark.skip("Scotch Bonnet")
def test_default_search_provider_change_awesome_bar(driver: Firefox):
    """
    C2860208 - This test makes sure that the default search provider can be changed and settings are applied
    """
    # Create objects
    nav = Navigation(driver)
    about_prefs = AboutPrefs(driver)

    # Make sure we start at about:newtab
    driver.get("about:newtab")

    # Click the USB and click the 'Search Settings' button.
    nav.open_searchmode_switcher_settings()

    # Set a different provider as a default search engine
    about_prefs.search_engine_dropdown().select_option("DuckDuckGo")

    # Open a new tab
    driver.get("about:newtab")

    # Verify that the search provider has been changed to the selected search engine
    nav.element_attribute_contains(
        "awesome-bar", "placeholder", "Search with DuckDuckGo or enter address"
    )
