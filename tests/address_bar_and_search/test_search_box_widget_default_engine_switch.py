import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "3897534"


def test_search_box_widget_default_engine_switch(driver: Firefox):
    about_prefs = AboutPrefs(driver, category="search")
    nav = Navigation(driver)

    # 1. Open about:preferences#search and set the default search engine to DuckDuckGo
    about_prefs.open()
    about_prefs.set_default_search_engine("DuckDuckGo")

    # 2. Verify the default search engine dropdown updated to DuckDuckGo
    assert "DuckDuckGo" in about_prefs.get_default_search_engine_label()

    # 3. Open a new tab and verify the URL bar's search widget reflects DuckDuckGo
    nav.open_new_tab_via_button()
    assert "DuckDuckGo" in nav.get_urlbar_switcher_label()
