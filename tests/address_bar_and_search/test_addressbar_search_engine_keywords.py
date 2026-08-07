import pytest
from selenium.webdriver import Firefox, Keys

from modules.browser_object_navigation import Navigation

ENGINE_KEYWORD = "@bing"
SEARCH_TERM = "mozilla"
SEARCH_ENGINE = "Bing"


@pytest.fixture()
def test_case():
    return "3028779"


def test_addressbar_search_engine_keywords(driver: Firefox):
    """
    C3028779 - Verify that addressbar results displays the correct search engine when searching
    with search engine keywords
    """

    nav = Navigation(driver)

    # Wait until Firefox has loaded the installed search engines.
    nav.click_search_mode_switcher()
    nav.element_visible(
        "search-mode-switcher-option",
        labels=[SEARCH_ENGINE],
    )
    nav.perform_key_combo_chrome(Keys.ESCAPE)
    nav.element_not_visible("legacy-searchbar-switcher-popup")

    nav.clear_awesome_bar()
    nav.type_in_awesome_bar(ENGINE_KEYWORD)

    # Give Firefox time to process the alias before entering the search term.
    nav.perform_key_combo_chrome(Keys.SPACE)
    nav.verify_search_mode_is_visible(SEARCH_ENGINE)

    nav.type_in_awesome_bar(SEARCH_TERM, reset=False)
    nav.verify_plain_text_in_input_awesome_bar(SEARCH_TERM)
    nav.verify_search_mode_is_visible(SEARCH_ENGINE)
