from pathlib import Path

import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs

PREFERENCE_STRING = 'user_pref("browser.privatebrowsing.autostart", true);'


@pytest.fixture()
def test_case():
    return "143604"


# make sure Firefox remembers history
@pytest.fixture()
def add_to_prefs_list():
    return [("browser.privatebrowsing.autostart", False)]


@pytest.fixture()
def about_prefs_category():
    return "privacy"


def test_never_remember_history(
    driver: Firefox, sys_platform: str, about_prefs: AboutPrefs
):
    """
    C143604: Make sure to set the pref via about:preferences, then check in about:config that the pref has been changed
    """
    about_prefs.open()

    # Change the settings to not remember the browser history
    about_prefs.set_history_option("dontremember")

    # The pref is only true while the "must restart" dialog is open, and any WebDriver
    # call would dismiss it, so read prefs.js off disk instead. Firefox writes the file
    # lazily (slowly on Windows), so poll until the pref shows up.
    prefs_file = Path(driver.capabilities["moz:profile"]) / "prefs.js"
    about_prefs.wait.until(
        lambda _: PREFERENCE_STRING in prefs_file.read_text(encoding="utf-8"),
        message=f"The preference {PREFERENCE_STRING} is not set correctly.",
    )
