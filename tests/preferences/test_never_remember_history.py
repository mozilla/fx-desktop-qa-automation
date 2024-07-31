import os
import time

import pytest
from selenium.webdriver import Firefox, Keys
from selenium.webdriver.common.by import By

from modules.browser_object_tabbar import TabBar
from modules.page_object import AboutNewtab, AboutPrefs


# make sure Firefox remembers history
@pytest.fixture()
def add_prefs():
    return [("browser.privatebrowsing.autostart", False)]


def test_never_remember_history(driver: Firefox, sys_platform: str):
    """
    C143604: Make sure to set the pref via about:preferences, then check in about:config that the pref has been changed
    """
    # instantiate objs
    AboutPrefs(driver, category="privacy").open()

    # Change the settings to not remember the browser history
    history_menulist = driver.find_element(By.ID, "historyMode")
    menulist_popup = history_menulist.find_element(By.TAG_NAME, "menupopup")
    options = menulist_popup.find_elements(By.TAG_NAME, "menuitem")

    # Scrolling for visibility
    driver.execute_script("arguments[0].scrollIntoView();", history_menulist)
    time.sleep(1)
    current_selection = history_menulist.get_attribute("value")

    if current_selection != "dontremember":
        for option in options:
            if option.get_attribute("value") == "dontremember":
                option.click()
                break

    # Verify that the pref is set to True
    profile_path = driver.capabilities['moz:profile']
    prefs_file_path = os.path.join(profile_path, 'prefs.js')

    # Read the contents of the 'prefs.js' file to check for the preference
    with open(prefs_file_path, 'r') as prefs_file:
        prefs_content = prefs_file.read()

    # Check that the preference is now True
    preference_string = 'user_pref("browser.privatebrowsing.autostart", true);'
    assert preference_string in prefs_content, f"The preference {preference_string} is not set correctly."
