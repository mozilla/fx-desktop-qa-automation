import pytest
from selenium.webdriver import Firefox

from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3028732"


def test_addressbar_search_engine_keywords(driver: Firefox):
    """
    C3028779 - Verify that addressbar results displays the correct search engine when searching with search engine keywords
    """

    # Instantiate objects
    prefs = AboutPrefs(driver, category="search")

    # Go to about:preferences#search
    prefs.open()

    # Add a keyword for one search engine (e.g. for Bing add "bn" keyword)

    # In the address bar type the keyword from step 3 and a search term (e.g. "bn mozilla")
