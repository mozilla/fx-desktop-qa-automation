import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import Navigation, TabBar
from modules.page_object import AboutConfig


@pytest.fixture()
def test_case():
    return "1365213"


# Set constants
SEARCH_BAR_PREF = "browser.search.widget.inNavBar"
SEARCH_TERM = "saxophone"


def test_search_bar_results(driver: Firefox):
    """
    C1365213 - The Search Bar provides valid results for specific search terms
    """

    # Create objects
    nav = Navigation(driver).open()
    ac = AboutConfig(driver)
    tab = TabBar(driver)

    # Check Google results from a Search bar search
    # First enable search bar via about:config
    ac.toggle_true_false_config(SEARCH_BAR_PREF)
    nav.clear_awesome_bar()

    # Then run search and check the results
    nav.search_bar_search(SEARCH_TERM)
    nav.set_content_context()
    tab.expect_title_contains("Google Search")
    search_url = driver.current_url
    assert SEARCH_TERM in search_url
    content_searchbar = nav.find_element(By.NAME, "q")
    content_searchbar_text = content_searchbar.get_attribute("value")
    assert content_searchbar_text == SEARCH_TERM
