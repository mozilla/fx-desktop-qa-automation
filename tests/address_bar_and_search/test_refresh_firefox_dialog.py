import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation


@pytest.fixture()
def test_case():
    return "2914620"


def test_refresh_firefox_dialog(driver: Firefox):
    """
    C2914620: Refresh Firefox dialog
    """
    # instantiate objects and type in search bar
    nav = Navigation(driver)
    nav.set_awesome_bar()
    nav.type_in_awesome_bar("refresh firefox")

    # Click on the "Refresh Firefox" button
    nav.click_on("refresh-button-awesome-bar")

    # Refresh Firefox dialog is correctly displayed
    nav.element_visible("refresh-firefox-dialog")