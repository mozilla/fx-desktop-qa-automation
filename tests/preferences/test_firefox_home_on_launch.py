import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.remote.webelement import WebElement

from modules.browser_object import PanelUi, TabBar
from modules.components.dropdown import Dropdown
from modules.page_object import AboutNewtab, AboutPrefs

import time


@pytest.fixture()
def test_case():
    return "143543"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.startup.homepage", "about:home"),
        ("browser.startup.blankWindow", "false"),
        ("browser.newtabpage.activity-stream.testing.shouldInitializeFeeds", "true")
    ]


@pytest.fixture()
def about_prefs_category():
    return "home"


@pytest.fixture()
def drop_down_root(about_prefs: AboutPrefs):
    about_prefs.open()
    return about_prefs.get_element("home-new-window-dropdown")


def test_firefox_home_on_launch(
    driver: Firefox,
    tabs: TabBar,
    about_new_tab: AboutNewtab,
    about_prefs: AboutPrefs,
    panel_ui: PanelUi,
    dropdown: Dropdown,
):
    """
    C143543: setting the default new window to be Firefox Home
    """

    # click the dropdown
    dropdown.select_option("Firefox Home (Default)")
    #dropdown.select_option("Firefox Home (Default)", double_click=True)

    # make sure that the option was selected correctly
    about_prefs.element_attribute_is(
        "home-new-window-dropdown", "label", "Firefox Home (Default)"
    )

    # open a new window
    panel_ui.open_and_switch_to_new_window("window")

    # make sure we are on the correct new window
    about_new_tab.element_exists("body-logo")
