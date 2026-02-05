import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.remote.webelement import WebElement

from modules.page_object import AboutNewtab


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
    dropdown.select_option("Firefox Home (Default)", double_click=True)

    # make sure that the option was selected correctly
    about_prefs.expect_element_attribute_is(
        "home-new-window-dropdown", "label", "Firefox Home (Default)"
    )

    # wait for the number of tabs and switch
    panel_ui.open_and_switch_to_new_window("window")

    # make sure we are on the correct new tab page
    assert about_new_tab.get_element("body-logo") is not None
