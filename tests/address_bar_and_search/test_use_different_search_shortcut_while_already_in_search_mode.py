import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation

SEARCH_ENGINE = "Wikipedia"
SEARCH_TERM = "@amazon"
URL_DOMAIN = "wikipedia.org"


@pytest.fixture()
def test_case():
    return "3028851"


def test_use_search_shortcut_for_a_different_search_engine_while_already_in_search_mode(
    driver: Firefox,
):
    """
    C3028851 - Verify that using a search shortcut for a different search engine while in search mode
    for another engine works as expected.
    """
    # Instantiate objects
    nav = Navigation(driver)

    # Enter search mode for the desired search engine in a new tab
    nav.open_and_switch_to_new_window("tab")
    nav.open_usb_and_select_option(SEARCH_ENGINE)

    # Verify search mode is entered for the corresponding engine
    nav.verify_search_mode_is_visible()

    # Type @engine shortcut
    nav.type_in_awesome_bar(SEARCH_TERM)

    # Verify the search mode label matches the selected search engine and the input contains the plain search term
    nav.verify_search_mode_label(SEARCH_ENGINE)
    nav.verify_plain_text_in_input_awesome_bar(SEARCH_TERM)

    # Perform the search by pressing Enter and expect
    nav.type_in_awesome_bar(Keys.ENTER)

    # Verify the domain is explicitly wikipedia.org
    nav.verify_domain(URL_DOMAIN)

    # Verify search term is also present in the URL
    nav.url_contains(SEARCH_TERM.lstrip("@"))
