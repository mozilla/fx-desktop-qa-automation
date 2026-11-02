import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation, TabBar

SEARCH_TERM = "Firefox"
SEARCH_ENGINES = [
    ("Google", "google", "google.com"),
    ("Bing", "bing", "bing.com"),
    ("DuckDuckGo", "duckduckgo", "duckduckgo.com"),
    ("eBay", "ebay", "ebay.com"),
    ("Perplexity", "perplexity", "perplexity.ai"),
    ("Wikipedia (en)", "wikipedia", "wikipedia.org"),
]


@pytest.fixture()
def test_case():
    return "3897531"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.search.widget.new", True)]


@pytest.mark.parametrize("engine, typed_text, domain", SEARCH_ENGINES)
def test_new_search_box_contextual_search(
    driver: Firefox, engine: str, typed_text: str, domain: str
):
    """
    C3897531 - Contextual search is functional from the new search box in a new tab.
    """
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Setup: add the search bar to the toolbar.
    nav.add_search_bar_via_customizable_ui()

    # Step 1: Type the engine name in the search box in a new tab.
    tabs.open_and_switch_to_new_tab()
    nav.type_in_search_bar(typed_text)
    nav.element_attribute_is("searchbar-input", "value", typed_text)
    nav.element_visible("searchbar-contextual-search-button", labels=[engine])

    # Step 2: Tab to the "Search with <engine>" button; search mode is entered.
    nav.perform_key_combo_chrome(Keys.TAB)
    nav.element_visible("searchbar-contextual-search-button-selected", labels=[engine])
    nav.element_attribute_contains(
        "legacy-searchmode-switcher-button", "aria-label", engine
    )

    # Step 3: Verify the search is performed without issue
    nav.type_in_search_bar(SEARCH_TERM + Keys.ENTER)
    nav.url_contains(domain)
    nav.url_contains(SEARCH_TERM)
