import pytest
from auto_fxui.browser_object import Navigation, TabBar
from selenium.webdriver import Firefox

ENGINE = "DuckDuckGo"
ENGINE_HOMEPAGE = "https://duckduckgo.com/"


@pytest.fixture()
def test_case():
    return "3897577"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.search.widget.new", True)]


def test_new_search_box_shift_click_engine_homepage(driver: Firefox):
    """C3897577 - Shift + Click on engines navigates to default SERP."""
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Setup: add the search bar to the toolbar.
    nav.add_search_bar_via_customizable_ui()

    # Steps 1-2: With the box empty, open the engine list and Shift + Click DDG.
    nav.search_bar_open_engine_search_form(ENGINE)

    # The engine homepage opens in the same tab.
    nav.url_contains(ENGINE_HOMEPAGE)
    tabs.wait_for_num_tabs(1)
