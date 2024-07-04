import time

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_about_prefs import AboutPrefs
from modules.util import BrowserActions


@pytest.fixture()
def add_prefs():
    return [
        ("browser.search.region", "US"),
    ]


def test_preferences_all_toggles_enabled(driver: Firefox):
    """
    C1618400: Preferences - All toggles buttons Enabled
    """
    # instantiate objects
    nav = Navigation(driver).open()
    about_prefs = AboutPrefs(driver, category="search").open()
    u = BrowserActions(driver)

    # Check if toggles are enabled
    nonsponsored_checkbox = about_prefs.get_element("firefox-suggest-nonsponsored")
    assert nonsponsored_checkbox.is_selected(), f"Checkbox with selector '{nonsponsored_checkbox}' is not checked"
    sponsors_checkbox = about_prefs.get_element("firefox-suggest-sponsored")
    assert sponsors_checkbox.is_selected(), f"Checkbox with selector '{sponsors_checkbox}' is not checked"

    # Check if sponsored suggestion is displayed
    time.sleep(20)
    u.search("iphone", with_enter=False)
    time.sleep(20)
    with (driver.context(driver.CONTEXT_CHROME)):
        assert nav.get_elements("sponsored-suggestion")

    # Check if a non-sponsored suggestion is displayed
    u.search("wiki", with_enter=False)
    with (driver.context(driver.CONTEXT_CHROME)):
        assert not nav.get_elements("sponsored-suggestion")