from urllib.parse import quote_plus

import pytest
from auto_fxui.browser_object import Navigation, TabBar
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

SEARCH_TERM = "mozilla"


@pytest.fixture()
def test_case():
    return "3897529"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.search.widget.new", True)]


def test_new_search_box_suggestions_present(driver: Firefox):
    """
    C3897529 - Search suggestions are present in the search box.
    """
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Setup: add the search bar to the toolbar.
    nav.add_search_bar_via_customizable_ui()

    # Step 1: Open a new tab and focus the search box.
    tabs.open_and_switch_to_new_tab()
    nav.click_on("searchbar-input")
    nav.verify_search_bar_is_focused()

    # Step 2: Type a string; suggestions show up.
    nav.type_in_search_bar(SEARCH_TERM)
    nav.search_bar_has_suggestions()

    # Step 3: Pick a suggestion and submit it.
    nav.perform_key_combo_chrome(Keys.DOWN)
    nav.verify_searchbar_suggestion_is_highlighted()
    suggestion = nav.get_search_bar_text()
    assert suggestion != SEARCH_TERM, "No suggestion was picked."
    nav.type_in_search_bar(Keys.ENTER)
    nav.url_contains(quote_plus(suggestion))
