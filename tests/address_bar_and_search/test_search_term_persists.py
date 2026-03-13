import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TabBar
from modules.page_object import AboutPrefs

SEARCH_ENGINE = "DuckDuckGo"
FIRST_SEARCH = "cheetah"
SECOND_SEARCH = "lion"


@pytest.fixture()
def test_case():
    return "3029211"


# Set search region
@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.urlbar.showSearchTerms.enabled", True),
        ("browser.urlbar.showSearchTerms.featureGate", True),
    ]


def test_search_term_persists(driver: Firefox):
    """
    C2153943 - Persist search term basic functionality
    """

    nav = Navigation(driver)
    tab = TabBar(driver)
    prefs = AboutPrefs(driver, category="search")

    # Set DuckDuckGo as default search engine
    nav.open_searchmode_switcher_settings()
    prefs.select_default_search_engine_by_key(SEARCH_ENGINE)

    # Perform a search using the URL bar
    driver.get("about:newtab")
    nav.search(FIRST_SEARCH)
    tab.expect_title_contains("DuckDuckGo")
    address_bar_text = nav.get_awesome_bar_text()
    assert FIRST_SEARCH == address_bar_text

    # Perform a new awesome bar search after navigating away
    nav.set_content_context()
    driver.get("about:robots")
    nav.search(SECOND_SEARCH)
    tab.expect_title_contains("DuckDuckGo")
    address_bar_text = nav.get_awesome_bar_text()
    assert SECOND_SEARCH == address_bar_text
