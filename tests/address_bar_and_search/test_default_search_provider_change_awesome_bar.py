import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "2860208"


# Scotch Bonnet -- uncomment after update
# @pytest.mark.ci
def test_default_search_provider_change_awesome_bar(driver: Firefox):
    """
    C2860208 - This test makes sure that the default search provider can be changed and settings are applied
    """
    # Create objects
    nav = Navigation(driver)
    search_term = "what is life?"

    # Make sure we start at about:newtab
    driver.get("about:newtab")

    # Type some word->select 'Change search settings' when the search drop-down panel is opened.
    nav.type_in_awesome_bar(search_term)
    nav.open_awesome_bar_settings()

    # Check that the current URL is about:preferences#search
    nav.expect_in_content(lambda _: driver.current_url == "about:preferences#search")

    # Open a site, open search settings again and check if it's opened in a different tab
    driver.get("https://9gag.com/")
    nav.type_in_awesome_bar(search_term)
    nav.open_awesome_bar_settings()

    driver.switch_to.window(driver.window_handles[1])
    nav.expect_in_content(lambda _: driver.current_url == "about:preferences#search")
    driver.switch_to.window(driver.window_handles[0])
    assert driver.current_url == "https://9gag.com/"

    # Set a different provider as a default search engine
    about_prefs = AboutPrefs(driver, category="search").open()
    about_prefs.search_engine_dropdown().select_option("DuckDuckGo")

    # Open the search bar and type in a keyword and check if it's with the right provider
    nav.search(search_term)
    nav.expect_in_content(lambda _: driver.current_url == "about:preferences#search")
    driver.quit()
