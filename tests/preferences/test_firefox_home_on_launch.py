import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi, TabBar
from modules.page_object import AboutNewtab, AboutPrefs


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return [
        ("browser.startup.homepage", "about:home"),
        ("browser.startup.blankWindow", "false"),
    ]


def test_firefox_home_on_launch(driver: Firefox, sys_platform: str):
    """
    C143543: setting the default new window to be Firefox Home
    """
    # instantiate objs
    tabs = TabBar(driver)
    new_tab = AboutNewtab(driver)
    about_prefs = AboutPrefs(driver, category="home").open()
    panel_ui = PanelUi(driver)

    # click the dropdown
    drop_down = about_prefs.get_element("home-new-window-dropdown")
    dropdown = about_prefs.Dropdown(page=about_prefs, root=drop_down)
    dropdown.select_option("Firefox Home (Default)", double_click=True)

    # make sure that the option was selected correctly
    assert drop_down.get_attribute("label") == "Firefox Home (Default)"
    panel_ui.open_panel_menu()
    panel_ui.select_panel_setting("panel-ui-new-window")
    # wait for the number of tabs and switch
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[-1])

    # make sure we are on the correct new tab page
    assert new_tab.get_element("body-logo") is not None
