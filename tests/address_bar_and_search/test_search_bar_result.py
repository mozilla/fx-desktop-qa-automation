import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation
from modules.page_object import AboutConfig


@pytest.fixture()
def add_prefs():
    return [
        ("browser.search.region", "US"),
    ]


def test_search_bar_results(driver: Firefox):
    """
    C1365213 - The Search Bar provides valid results for specific search terms
    """

    # Create objects
    nav = Navigation(driver).open()
    ac = AboutConfig(driver)

    search_term = "saxophone"

    # Check Google results from a Search bar search
    # First enable search bar via about:config
    pref = "browser.search.widget.inNavBar"
    ac.toggle_true_false_config(pref)
    nav.clear_awesome_bar()

    # Then run search and check the results
    nav.search_bar_search(search_term)
    nav.set_content_context()
    nav.expect_in_content(EC.title_contains("Google Search"))
    search_url = driver.current_url
    assert search_term in search_url
    content_searchbar = nav.find_element(By.NAME, "q")
    content_searchbar_text = content_searchbar.get_attribute("value")
    assert content_searchbar_text == search_term
