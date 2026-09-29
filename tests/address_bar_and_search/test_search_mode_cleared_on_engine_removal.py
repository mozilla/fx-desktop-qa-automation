import pytest
from pytest_httpserver import HTTPServer

from modules.browser_object import Navigation
from modules.page_object import AboutPrefs

SEARCH_ENGINE = "Starfox Search"


@pytest.fixture()
def test_case():
    return "3028844"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.settings-redesign.enabled", True)]


@pytest.fixture()
def engine_url(httpserver: HTTPServer) -> str:
    httpserver.expect_request("/search").respond_with_data(
        "<html><body>Starfox results</body></html>", content_type="text/html"
    )
    return httpserver.url_for("/search") + "?q=%s"


def test_search_mode_cleared_on_engine_removal(driver, engine_url: str):
    """
    C3028844 - Verify that removing a search engine from about:preferences#search
    clears search mode if that engine is currently selected in search mode in a different tab.
    """
    # Instantiate objects
    nav = Navigation(driver)
    prefs = AboutPrefs(driver, category="search")

    # Built-in engines can only be disabled in the redesigned settings.
    prefs.open()
    prefs.add_search_engine(SEARCH_ENGINE, engine_url, "@starfox")
    prefs.scroll_to_element("search-shortcuts-engine-row", labels=[SEARCH_ENGINE])
    prefs.element_visible("search-shortcuts-engine-row", labels=[SEARCH_ENGINE])

    # Enter search mode for the desired search engine in a new tab
    nav.open_and_switch_to_new_window("tab")
    search_tab = driver.current_window_handle
    nav.set_search_mode(SEARCH_ENGINE)

    # Verify search mode is entered for the corresponding engine
    nav.verify_search_mode_is_visible(SEARCH_ENGINE)

    # In another tab, remove that search engine from about:preferences#search
    nav.open_and_switch_to_new_window("tab")
    prefs.open()
    prefs.remove_search_engine(SEARCH_ENGINE)

    # Return to the tab that was using the removed engine.
    driver.switch_to.window(search_tab)
    nav.verify_search_mode_is_not_visible(SEARCH_ENGINE)
