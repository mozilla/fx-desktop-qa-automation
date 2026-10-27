from pathlib import Path

import pytest
from pytest_httpserver import HTTPServer
from selenium.webdriver import Firefox

from auto_fxui.browser_object import Navigation
from auto_fxui.page_object import AboutPrefs
from auto_fxui.page_object_generics import GenericPage

SEARCH_ENGINE = "Starfox Search"
LOCAL_HTML = "open_search_page.html"
LOCAL_OSDX = "open_search.osdx"


@pytest.fixture()
def test_case():
    return "3897545"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.search.widget.new", True),
        ("browser.settings-redesign.enabled", True),
    ]


@pytest.fixture()
def test_url():
    """Serve a page that offers a search engine, over http so Firefox can add it."""
    # Own server on a free port: xdist workers can't share the suite's port 5312.
    server = HTTPServer(host="127.0.0.1", port=0)
    server.start()
    pages = Path("data/pages")
    osdx = (pages / LOCAL_OSDX).read_text(encoding="utf-8")
    server.expect_request(f"/{LOCAL_HTML}").respond_with_data(
        (pages / LOCAL_HTML).read_text(encoding="utf-8"), content_type="text/html"
    )
    # OpenSearch needs a full search URL, so fill in this server's.
    server.expect_request(f"/{LOCAL_OSDX}").respond_with_data(
        osdx.replace("{search_url}", server.url_for("/search")),
        content_type="application/opensearchdescription+xml",
    )
    yield server.url_for(f"/{LOCAL_HTML}")
    server.stop()


def test_new_search_box_add_open_search_engine(driver: Firefox, test_url: str):
    """C3897545 - Open search engines can be added from the new search box."""
    nav = Navigation(driver)
    prefs = AboutPrefs(driver, category="search")
    page = GenericPage(driver, url=test_url)

    # Setup: add the search bar to the toolbar.
    nav.add_search_bar_via_customizable_ui()

    # Step 1: Open a site that offers a search engine.
    page.open()

    # Step 2: Open the engine dropdown in the search box.
    nav.click_on("legacy-searchmode-switcher")

    # Step 3: Click the "Add" option for the engine.
    nav.element_clickable("search-mode-add-option", labels=[SEARCH_ENGINE])
    nav.js_click_on("search-mode-add-option", labels=[SEARCH_ENGINE])

    # Step 4: The engine shows in Search Shortcuts.
    prefs.open()
    prefs.scroll_to_element("search-shortcuts-engine-row", labels=[SEARCH_ENGINE])
    prefs.element_visible("search-shortcuts-engine-row", labels=[SEARCH_ENGINE])
