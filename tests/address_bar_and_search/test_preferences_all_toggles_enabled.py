
import time

import pytest
from selenium.common import NoSuchElementException
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_about_newtab import AboutNewtab
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
    tabs = TabBar(driver)

    # Check if toggles are enabled
    nonsponsored_checkbox = about_prefs.get_element("firefox-suggest-nonsponsored")
    assert nonsponsored_checkbox.is_selected(), f"Checkbox with selector '{nonsponsored_checkbox}' is not checked"
    sponsors_checkbox = about_prefs.get_element("firefox-suggest-sponsored")
    assert sponsors_checkbox.is_selected(), f"Checkbox with selector '{sponsors_checkbox}' is not checked"

    # Check if sponsored suggestion is displayed
    tabs.new_tab_by_button()
    tabs.switch_tab()
    time.sleep(20)
    u.search("iphone", with_enter=False)
    time.sleep(5)
    with (driver.context(driver.CONTEXT_CHROME)):
        firefox_suggest = nav.get_element("firefox-suggestion")
        # .get_attribute("Sponsored")
        # sponsored = firefox_suggest.get_attribute("Sponsored")
        # expected_attribute = "Sponsored"
        assert firefox_suggest.is_displayed()
    # sponsored = firefox_suggest.get_attribute("Sponsored")
    # assert firefox_suggest.is_displayed()

    # Check if a non-sponsored suggestion is displayed
    nav.clear_awesome_bar()
    time.sleep(20)
    u.search("wikipedia", with_enter=False)
    # nav.type_in_awesome_bar("wikipedia")
    time.sleep(20)
    try:
        with (driver.context(driver.CONTEXT_CHROME)):
            firefox_suggest = nav.get_element("firefox-suggestion")
            is_displayed = firefox_suggest.is_displayed()
    except NoSuchElementException:
        is_displayed = False
    assert not is_displayed, f"Element with XPath {firefox_suggest} is displayed, but it should not be."
