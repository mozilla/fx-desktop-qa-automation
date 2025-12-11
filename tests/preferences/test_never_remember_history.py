import os
import time

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "143604"


# make sure Firefox remembers history
@pytest.fixture()
def add_to_prefs_list():
    return [("browser.privatebrowsing.autostart", False)]


def test_never_remember_history(driver: Firefox, sys_platform: str):
    """
    C143604: Make sure to set the pref via about:preferences, then check in about:config that the pref has been changed
    """
    about_prefs = AboutPrefs(driver, category="privacy").open()

    # Change the settings to not remember the browser history
    about_prefs.set_history_option("dontremember")

    # Verify that the pref is set to True
    profile_path = driver.capabilities["moz:profile"]
    prefs_file_path = os.path.join(profile_path, "prefs.js")

    # Read the contents of the 'prefs.js' file to check for the preference
    with open(prefs_file_path, "r") as prefs_file:
        prefs_content = prefs_file.read()

    # Check that the preference is now True
    preference_string = 'user_pref("browser.privatebrowsing.autostart", true);'
    assert preference_string in prefs_content, (
        f"The preference {preference_string} is not set correctly."
    )
