import pytest
from pytest_httpserver import HTTPServer
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation, TabBar
from modules.page_object import AboutPrefs
from modules.page_object_generics import GenericPage

SEARCH_ENGINE = "Starfox Search"
ENGINE_KEYWORD = "@starfox"
SEARCH_TERM = "mozilla"
PAGE_TITLE = "Starfox page"


@pytest.fixture()
def test_case():
    return "3897583"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.search.widget.new", True),
        # Step 1: Set browser.search.openintab to true.
        ("browser.search.openintab", True),
        ("browser.settings-redesign.enabled", True),
    ]


@pytest.fixture()
def test_url(httpserver: HTTPServer) -> str:
    httpserver.expect_request("/page").respond_with_data(
        f"<html><head><title>{PAGE_TITLE}</title></head><body>Starfox page</body></html>",
        content_type="text/html",
    )
    return httpserver.url_for("/page")


@pytest.fixture()
def engine_url(httpserver: HTTPServer) -> str:
    httpserver.expect_request("/search").respond_with_data(
        "<html><body>Starfox results</body></html>", content_type="text/html"
    )
    return httpserver.url_for("/search") + "?q=%s"


def test_new_search_box_opens_results_in_new_tab(
    driver: Firefox, test_url: str, engine_url: str
):
    """
    C3897583 - The new search box opens results in a new tab if
    browser.search.openintab is set to true.
    """
    nav = Navigation(driver)
    tabs = TabBar(driver)
    prefs = AboutPrefs(driver, category="search")
    page = GenericPage(driver, url=test_url)

    # Setup: add the search bar and use a local engine, so no captcha.
    nav.add_search_bar_via_customizable_ui()
    prefs.open()
    prefs.add_search_engine(SEARCH_ENGINE, engine_url, ENGINE_KEYWORD)
    prefs.select_default_search_engine_by_key(SEARCH_ENGINE)

    # Step 2: On a website, search from the search box.
    page.open()
    nav.type_in_search_bar(SEARCH_TERM)
    nav.perform_key_combo_chrome(Keys.ENTER)

    # The search opens in a new tab and the website stays in the first one.
    tabs.wait_for_num_tabs(2)
    tabs.switch_to_new_tab()
    nav.url_contains(f"/search?q={SEARCH_TERM}")
    tabs.element_attribute_is("tab-by-index", "label", PAGE_TITLE, labels=["1"])
