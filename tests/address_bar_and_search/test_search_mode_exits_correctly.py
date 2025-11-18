from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation


TEXT = "Firefox"
SEARCH_ENGINE = "Bing"
DEFAULT_ENGINE = "Google"


@pytest.fixture()
def test_case():
    return "3028848"


def test_search_mode_exits_correctly(driver: Firefox):
    """
    C3028848: Search mode is correctly exited
    """

    # Instantiate objects
    nav = Navigation(driver)

    # Open a new tab, focus the urlbar, type some text, and choose an engine from the USB
    nav.type_in_awesome_bar(TEXT)
    nav.click_search_mode_switcher()
    nav.set_search_mode("Bing")

    # Check that the search engine is shown
    nav.verify_engine_returned(SEARCH_ENGINE)

    # Hover over the engine name and click on the close button
    nav.click_exit_button_searchmode()

    # Check that search mode is exited and new suggestions(default engine) are returned
    nav.verify_engine_returned(DEFAULT_ENGINE)
