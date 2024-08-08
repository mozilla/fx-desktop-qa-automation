import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TabBar
from modules.page_object import AboutConfig


# Set search region
@pytest.fixture()
def add_prefs():
    return [
        ("browser.urlbar.showSearchTerms.enabled", True),
        ("browser.urlbar.showSearchTerms.featureGate", True),
    ]


# Set constants
FIRST_SEARCH = "cheetah"
FIRST_RESULT = "https://www.google.com/search?client=firefox-b-1-d&q=cheetah"
SECOND_SEARCH = "lion"


def test_search_term_persists(driver: Firefox):
    """
    C2153943 - Persist search term basic functionality
    """

    # Create objects
    nav = Navigation(driver).open()
    tab = TabBar(driver)

    # Perform a search using the URL bar.
    nav.search(FIRST_SEARCH)
    tab.expect_title_contains("Google Search")
    address_bar_text = nav.get_awesome_bar_text()
    assert FIRST_SEARCH == address_bar_text

    # Perform a new awesome bar search, full url should be present
    # First, navigate away from Google
    nav.set_content_context()
    driver.get("about:robots")
    # Then perform another search
    nav.search(SECOND_SEARCH)
    tab.expect_title_contains("Google Search")
    address_bar_text = nav.get_awesome_bar_text()
    assert SECOND_SEARCH == address_bar_text
