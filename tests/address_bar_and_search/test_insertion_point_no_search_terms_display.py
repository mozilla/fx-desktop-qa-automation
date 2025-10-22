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
    nav.perform_key_combo(Keys.BACKSPACE)

    # check that the selected engine is returned to using default engine

    # Type anything in the url bar (example moza)
