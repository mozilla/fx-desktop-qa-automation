import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.components.dropdown import Dropdown
from modules.page_object import AboutNewtab, AboutPrefs


@pytest.fixture()
def test_case():
    return "161472"


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
    about_prefs.expect_element_attribute_is(
        "home-new-window-dropdown", "label", "Firefox Home (Default)"
    )

    # wait for the number of tabs and switch
    tabs.open_and_switch_to_new_tab()

    # make sure we are on the correct new tab page
    assert about_new_tab.get_element("body-logo") is not None
