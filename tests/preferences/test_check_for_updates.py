import pytest
from selenium.webdriver import Firefox

from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "143572"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("app.update.disabledForTesting", False)]


def test_check_for_updates(driver: Firefox, about_prefs: AboutPrefs):
    """
    C143572 - The check for updates button is available and responsive
    The Button changes text to "Restart to update" if an update is available
    """

    about_prefs.open()

    # Find the 'updateButton' and 'checkForUpdatesButton3' elements
    # verify that they are interactable with the correct text.
    about_prefs.verify_element_is_interactable(
        "update_available_button", "Restart to Update Firefox"
    )
    about_prefs.verify_element_is_interactable("up_to_date_button", "Check for updates")
