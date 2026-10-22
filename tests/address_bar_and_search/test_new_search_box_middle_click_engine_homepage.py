import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TabBar

ENGINE = "DuckDuckGo"
ENGINE_HOMEPAGE = "https://duckduckgo.com/"
SEARCH_TERM = "mozilla"


@pytest.fixture()
def test_case():
    return "3897588"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.search.widget.new", True)]


def test_new_search_box_middle_click_engine_homepage(driver: Firefox):
    """C3897588 - Search bar middle click opens the engine home page."""
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Setup: add the search bar to the toolbar.
    nav.add_search_bar_via_customizable_ui()

    # Step 1: With the box empty, open the engine list and middle click DDG.
    nav.click_on("searchbar-input")
    nav.search_bar_middle_click_engine(ENGINE)

    # The engine home page opens in a new tab, with no search.
    tabs.wait_for_num_tabs(2)
    tabs.switch_to_new_tab()
    nav.url_contains(ENGINE_HOMEPAGE)

    # Step 2: Type a term, open the engine list and middle click DDG.
    nav.type_in_search_bar(SEARCH_TERM)
    nav.search_bar_middle_click_engine(ENGINE)

    # The DDG SERP opens in another new tab.
    tabs.wait_for_num_tabs(3)
    tabs.switch_to_new_tab()
    nav.url_contains(ENGINE_HOMEPAGE)
    nav.url_contains(f"q={SEARCH_TERM}")
