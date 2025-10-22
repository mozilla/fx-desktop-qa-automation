import pytest
from selenium.webdriver import Firefox, Keys

from modules.browser_object_navigation import Navigation


@pytest.fixture()
def test_case():
    return "3028716"


@pytest.mark.parametrize("engine", ["Bing"])
def test_insertion_point_no_search_terms_display(driver: Firefox, engine):
    """
    C3028716 - Verify that Insertion Point without search terms is correctly displayed
    """

    # Instantiate objects
    nav = Navigation(driver)

    # Click on the USB and select one of the engines
    nav.click_search_mode_switcher()
    nav.set_search_mode(engine)

    # Click on the url bar
    nav.click_in_awesome_bar()

    # Press [backspace/Delete in macOS]
    nav.perform_key_combo_chrome(Keys.BACKSPACE)

    # check that the selected engine is returned to using default engine
    nav.verify_engine_returned_default()

    # Type anything in the url bar (example moza)
    nav.type_in_awesome_bar("moza")

    # check that there is no Bing "Search Mode", search suggestions populate with default engine
    nav.verify_engine_returned_default()

    # Press enter key
    nav.perform_key_combo_chrome(Keys.ENTER)

    # Check that the search is done for "moza" using the default search engine
    nav.verify_engine_returned_default()