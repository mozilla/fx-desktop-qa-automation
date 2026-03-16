import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TabBar
from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "3029211"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.urlbar.showSearchTerms.enabled", True),
        ("browser.urlbar.showSearchTerms.featureGate", True),
    ]


SEARCH_ENGINE = "DuckDuckGo"
FIRST_SEARCH = "cheetah"
SECOND_SEARCH = "lion"


def test_search_term_persists(driver: Firefox):
    """
    C2153943 - Persist search term basic functionality
    """

    nav = Navigation(driver)
    tab = TabBar(driver)
    prefs = AboutPrefs(driver, category="search")

    prefs.open()
    prefs.select_default_search_engine_by_key(SEARCH_ENGINE)

    nav.search(FIRST_SEARCH)
    tab.expect_title_contains(SEARCH_ENGINE)
    address_bar_text = nav.get_awesome_bar_text()
    assert FIRST_SEARCH == address_bar_text

    nav.set_content_context()
    driver.get("about:robots")

    nav.search(SECOND_SEARCH)
    tab.expect_title_contains(SEARCH_ENGINE)
    address_bar_text = nav.get_awesome_bar_text()
    assert SECOND_SEARCH == address_bar_text
