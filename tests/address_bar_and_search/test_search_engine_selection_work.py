import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar

# Wikipedia redirects exact article matches to /wiki/<Title>; the capitalized
# term keeps the URL check valid there as well.
SEARCH_TERM = "Firefox"
SEARCH_ENGINES = {
    "Google": "google.com",
    "Bing": "bing.com",
    "DuckDuckGo": "duckduckgo.com",
    "eBay": "ebay.com",
    "MDN": "developer.mozilla.org",
    "Perplexity": "perplexity.ai",
    "Wikipedia (en)": "wikipedia.org",
}


@pytest.fixture()
def test_case():
    return "3897527"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.search.widget.new", True)]


@pytest.mark.parametrize("search_engine", SEARCH_ENGINES)
def test_search_engine_selection_work(driver: Firefox, search_engine: str):
    """
    C3897527 - Test the search engine selection from search bar works correctly and
    search is made without issue
    """
    nav = Navigation(driver)
    tab = TabBar(driver)
    nav.add_search_bar_via_customizable_ui()

    # type the search term into search bar and check it's visible
    tab.open_and_switch_to_new_tab()
    nav.type_in_search_bar(SEARCH_TERM)
    nav.element_attribute_is("searchbar-input", "value", SEARCH_TERM)

    # pick the search engine from the search bar switcher
    nav.click_on("legacy-searchmode-switcher")
    nav.element_clickable("search-mode-switcher-option", labels=[search_engine])
    nav.js_click_on("search-mode-switcher-option", labels=[search_engine])
    nav.element_attribute_is(
        "legacy-searchmode-switcher-title", "textContent", search_engine
    )

    nav.type_in_search_bar(Keys.ENTER)

    nav.url_contains(SEARCH_ENGINES[search_engine])
    nav.url_contains(SEARCH_TERM)
