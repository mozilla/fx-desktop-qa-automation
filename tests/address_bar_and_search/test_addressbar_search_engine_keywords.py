import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation


TEXT = "@bing mozilla"
SEARCH_ENGINE = "Bing"


@pytest.fixture()
def test_case():
    return "3028779"


def test_addressbar_search_engine_keywords(driver: Firefox):
    """
    C3028779 - Verify that addressbar results displays the correct search engine when searching with search engine keywords
    """

    # Instantiate objects
    nav = Navigation(driver)

    # TODO: Add a keyword for one search engine (e.g. for Bing add "bn" keyword) and search for (e.g. "bn mozilla")

    # In the address bar type the default search engine keyword and a search term (e.g. "@bing mozilla")
    nav.type_in_awesome_bar(TEXT)

    # Results from URL bar state that the search will be performed with "Bing" (e.g. "mozilla - Search with Bing")
    nav.verify_engine_returned(SEARCH_ENGINE)
