import pytest
from auto_fxui.browser_object import Navigation, TabBar
from auto_fxui.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "3897534"


def test_search_box_widget_default_engine_switch(driver):
    """
    C3897534 - Verify that changing the default search engine is reflected into the new search box widget
    """
    about_prefs = AboutPrefs(driver, category="search").open()
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # 1. Select DuckDuckGo as the default search engine in about:preferences#search
    about_prefs.search_engine_dropdown().select_option("DuckDuckGo")

    # 2. Verify the default search engine updated to DuckDuckGo
    about_prefs.wait_for_default_search_engine("DuckDuckGo")

    # 3. Open a new tab and verify the URL bar search mode switcher reflects DuckDuckGo
    tabs.new_tab_by_button()
    nav.verify_search_mode_is_visible("DuckDuckGo")
