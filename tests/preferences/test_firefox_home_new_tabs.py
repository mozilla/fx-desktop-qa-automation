import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.components.dropdown import Dropdown
from modules.page_object import AboutNewtab, AboutPrefs


@pytest.fixture()
def test_case():
    return "161472"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.newtabpage.activity-stream.testing.shouldInitializeFeeds", "true")
    ]


@pytest.fixture()
def about_prefs_category():
    return "home"


def test_firefox_home_new_tab(
    driver: Firefox,
    about_prefs: AboutPrefs,
    tabs: TabBar,
    about_new_tab: AboutNewtab,
    dropdown: Dropdown,
):
    """
    C161472: setting the default new window to be Firefox Home
    """

    # click the dropdown
    dropdown.select_option("Firefox Home (Default)")

    # make sure that the option was selected correctly
    about_prefs.element_attribute_is(
        "home-new-tabs-dropdown", "label", "Firefox Home (Default)"
    )

    # open a new tab
    tabs.open_and_switch_to_new_tab()

    # make sure we are on the correct new tab page
    about_new_tab.element_exists("body-logo")
