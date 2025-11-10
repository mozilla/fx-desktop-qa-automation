import sys

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3028905"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.urlbar.suggest.topsites", False)]


SEARCH_TERMS = ["alpha test", "beta test", "gamma test"]


def test_suggestions_for_empty_query_not_shown_in_search_mode(driver: Firefox):
    """
    Step 1: Create search history for Google (3 terms)
        Change default engine to DuckDuckGo
    Step 2: Use the search mode switcher to select eBay with EMPTY input.
        Search mode for eBay is shown; no dropdown suggestions appear.
    Step 3: Open a new tab and press Ctrl/Cmd+K.
        No dropdown history is shown for the current default search engine(DuckDuckgo)
    """
    nav = Navigation(driver)
    prefs = AboutPrefs(driver, category="search")

    # Step 1: Create Google search history with 3 queries
    for term in SEARCH_TERMS:
        nav.open_and_switch_to_new_window("tab")
        nav.clear_awesome_bar()
        nav.search("@google")
        nav.type_in_awesome_bar(term + Keys.ENTER)

    # Change default search engine to DuckDuckGo
    nav.open_and_switch_to_new_window("tab")
    prefs.open()
    prefs.search_engine_dropdown().select_option("DuckDuckGo")

    # Switch to eBay (empty query)
    nav.open_and_switch_to_new_window("tab")
    nav.clear_awesome_bar()
    nav.click_search_mode_switcher()
    nav.set_search_mode("eBay")

    # Verify there are no suggestions for an empty query in DuckDuckGo mode
    has_no_external_suggestions = nav.verify_no_external_suggestions(
        text="", search_mode="awesome", max_rows=0
    )
    assert has_no_external_suggestions, (
        "Suggestions are displayed for an empty query when in DuckDuckGo search mode."
    )

    # --- Step 3: New tab + Ctrl/Cmd+K; verify no dropdown history is shown
    nav.open_and_switch_to_new_window("tab")
    nav.clear_awesome_bar()

    actions = ActionChains(driver)
    if sys.platform == "darwin":
        actions.key_down(Keys.COMMAND).send_keys("k").key_up(Keys.COMMAND).perform()
    else:
        actions.key_down(Keys.CONTROL).send_keys("k").key_up(Keys.CONTROL).perform()

    has_no_external_suggestions = nav.verify_no_external_suggestions(
        text="", search_mode="awesome", max_rows=0
    )
    assert has_no_external_suggestions, (
        "Search history suggestions are displayed after Ctrl/Cmd+K with an empty query."
    )
