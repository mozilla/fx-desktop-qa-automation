import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.remote.webelement import WebElement

from modules.browser_object import PanelUi, TabBar
from modules.components.dropdown import Dropdown
from modules.page_object import AboutNewtab, AboutPrefs


@pytest.fixture()
def test_case():
    return "143543"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.startup.homepage", "about:home"),
        ("browser.startup.blankWindow", "false"),
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
    sys_platform: str,
    tabs: TabBar,
    about_new_tab: AboutNewtab,
    about_prefs: AboutPrefs,
    panel_ui: PanelUi,
    dropdown: Dropdown,
    drop_down_root: WebElement,
):
    """
    C143543: setting the default new window to be Firefox Home
    """
    about_prefs.open()

    # click the dropdown
    drop_down = about_prefs.get_element("home-new-window-dropdown")
    dropdown.select_option("Firefox Home (Default)", double_click=True)

    # make sure that the option was selected correctly
    assert drop_down.get_attribute("label") == "Firefox Home (Default)"

    # wait for the number of tabs and switch
    panel_ui.open_and_switch_to_new_window("window")

    # make sure we are on the correct new tab page
    assert about_new_tab.get_element("body-logo") is not None
