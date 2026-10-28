from pathlib import Path

import pytest
from auto_fxui.browser_object import Navigation, TabBar
from auto_fxui.page_object import AboutPrefs
from auto_fxui.page_object_generics import GenericPage
from pytest_httpserver import HTTPServer
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

SEARCH_ENGINE = "Starfox Search"
SEARCH_TERM = "mozilla"
LOCAL_HTML = "open_search_page.html"
LOCAL_OSDX = "open_search.osdx"


@pytest.fixture()
def test_case():
    return "3897547"


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
    server.expect_request("/search").respond_with_data(
        "<html><body>Starfox results</body></html>", content_type="text/html"
    )
    yield server.url_for(f"/{LOCAL_HTML}")
    server.stop()


def test_new_search_box_added_engine_default(driver: Firefox, test_url: str):
    """C3897547 - Engines added from the new search box can be made default."""
    nav = Navigation(driver)
    tabs = TabBar(driver)
    prefs = AboutPrefs(driver, category="search")
    page = GenericPage(driver, url=test_url)

    # Setup: add the search bar to the toolbar.
    nav.add_search_bar_via_customizable_ui()

    # Step 1: Open a site that offers a search engine.
    page.open()

    # Steps 2-3: Add the engine from the search box dropdown.
    nav.click_on("legacy-searchmode-switcher")
    nav.element_clickable("search-mode-add-option", labels=[SEARCH_ENGINE])
    nav.js_click_on("search-mode-add-option", labels=[SEARCH_ENGINE])

    # Step 4: Make the engine the default.
    prefs.open()
    prefs.select_default_search_engine_by_key(SEARCH_ENGINE)

    # Step 5: Open a new tab and focus the search box.
    tabs.open_and_switch_to_new_tab()
    nav.click_on("searchbar-input")
    nav.verify_search_bar_is_focused()

    # Step 6: Search uses the new engine.
    nav.type_in_search_bar(SEARCH_TERM)
    nav.perform_key_combo_chrome(Keys.ENTER)
    nav.url_contains(f"/search?q={SEARCH_TERM}")
