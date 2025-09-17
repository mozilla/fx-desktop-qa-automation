import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation

SEARCH_QUERY = "refresh firefox"
REFRESH_BUTTON_ID = "refresh-button-awesome-bar"
DIALOG_ID = "refresh-firefox-dialog"


@pytest.fixture()
def test_case():
    return "3028765"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.profiles.enabled", True)]


@pytest.fixture()
def use_profile():
    return "theme_change"


def test_refresh_firefox_dialog(driver: Firefox):
    """
    C2914620 - Verify that the 'Refresh Firefox' dialog appears from the address bar.
    """
    nav = Navigation(driver)
    nav.type_in_awesome_bar(SEARCH_QUERY)

    # Bug 1928138 will restore Refresh Fx for some profiles
    nav.element_does_not_exist(REFRESH_BUTTON_ID)
    # nav.element_visible(DIALOG_ID)
