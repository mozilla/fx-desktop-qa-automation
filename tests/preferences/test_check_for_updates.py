import time

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object_about_prefs import AboutPrefs


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return [("app.update.disabledForTesting", False)]


def test_check_for_updates(driver: Firefox):
    """
    C143572 - The check for updates button is available and responsive
    The Button changes text to "Restart to update" if an update is available
    """

    Navigation(driver).open()
    about_prefs = AboutPrefs(driver, category="general").open()
    time.sleep(2)

    # Find the 'updateButton' and 'checkForUpdatesButton3' elements
    update_available_button = about_prefs.get_element("update_available_button")
    up_to_date_button = about_prefs.get_element("up_to_date_button")
    time.sleep(2)

    # Check the label of the buttons and assert they are correct
    if update_available_button.is_displayed():
        label = update_available_button.text
        assert (
            label == "Restart to Update Firefox"
        ), f"Expected label to be 'Restart to Update Firefox' but got '{label}'"
        assert (
            update_available_button.is_enabled()
        ), "The 'Restart to Update Firefox' button is not clickable"
    elif up_to_date_button.is_displayed():
        label = up_to_date_button.text
        assert (
            label == "Check for updates"
        ), f"Expected label to be 'Check for updates' but got '{label}'"
        assert (
            up_to_date_button.is_enabled()
        ), "The 'Check for updates' button is not clickable"
