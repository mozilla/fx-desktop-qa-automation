import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
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
):
    """
    C161472 - Verify that Firefox can be set to display Firefox Home in new tab
    """

    # Open preferences and select Firefox Home from the new tabs dropdown
    about_prefs.open()
    about_prefs.select_new_tabs_firefox_home()

    # make sure that the option was selected correctly
    about_prefs.element_attribute_is(
        "homepage-new-tabs-dropdown", "value", "home"
    )

    # open a new tab
    tabs.open_and_switch_to_new_tab()

    # verify the new tab URL
    about_new_tab.url_contains("about:newtab")

    # make sure we are on the correct new tab page
    about_new_tab.element_exists("body-logo")
