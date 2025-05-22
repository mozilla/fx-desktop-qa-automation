import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation

SEARCH_QUERY = "refresh firefox"
REFRESH_BUTTON_ID = "refresh-button-awesome-bar"
DIALOG_ID = "refresh-firefox-dialog"


@pytest.fixture()
def test_case():
    return "3028765"


def test_refresh_firefox_dialog(driver: Firefox):
    """
    C2914620 - Verify that the 'Refresh Firefox' dialog appears from the address bar.
    """
    nav = Navigation(driver)
    nav.set_awesome_bar()
    nav.type_in_awesome_bar(SEARCH_QUERY)

    nav.click_on(REFRESH_BUTTON_ID)
    nav.element_visible(DIALOG_ID)
