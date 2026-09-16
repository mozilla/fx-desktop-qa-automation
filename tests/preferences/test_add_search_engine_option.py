import pytest
from pytest_httpserver import HTTPServer
from selenium.webdriver import Firefox, Keys

from modules.browser_object import Navigation, TabBar
from modules.page_object import AboutPrefs, GenericPage

ENGINE_NAME = "Starfox Search"
ENGINE_KEYWORD = "@starfox"
SEARCH_TERM = "hello"
RESULTS_TEXT = "Starfox results"


@pytest.fixture()
def about_prefs_category():
    return "search"


@pytest.fixture()
def test_case():
    return "4105790"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.settings-redesign.enabled", True)]


@pytest.fixture()
def engine_url(httpserver: HTTPServer) -> str:
    """Serve a stand-in results page, %s is where the search term goes."""
    httpserver.expect_request("/search").respond_with_data(
        f"<html><body><h1>{RESULTS_TEXT}</h1></body></html>", content_type="text/html"
    )
    return httpserver.url_for("/search") + "?q=%s"


def test_add_search_engine_option(
    driver: Firefox,
    about_prefs: AboutPrefs,
    nav: Navigation,
    tabs: TabBar,
    engine_url: str,
):
    """
    C4105790 - The Add search engine option works as expected.
    """
    # Steps 1, 2 and 3: Add an engine from the Search settings.
    about_prefs.open()
    about_prefs.add_search_engine(ENGINE_NAME, engine_url, ENGINE_KEYWORD)

    # The new engine is listed with the other engines, under its keyword.
    about_prefs.element_visible(
        "search-shortcuts-added-engine", labels=[ENGINE_NAME, ENGINE_KEYWORD]
    )

    # Step 4: Search with the new engine in a new tab.
    tabs.open_and_switch_to_new_tab()
    nav.type_in_awesome_bar(ENGINE_KEYWORD)
    # Give Firefox time to process the alias before entering the search term.
    nav.perform_key_combo_chrome(Keys.SPACE)
    nav.verify_search_mode_is_visible(ENGINE_NAME)
    nav.type_in_awesome_bar(SEARCH_TERM + Keys.ENTER, reset=False)

    # The engine's URL was used, with the term in place of %s.
    results_page = GenericPage(driver, url=engine_url.replace("%s", SEARCH_TERM))
    results_page.url_contains(f"q={SEARCH_TERM}")
    results_page.element_has_text("page-body", RESULTS_TEXT)
