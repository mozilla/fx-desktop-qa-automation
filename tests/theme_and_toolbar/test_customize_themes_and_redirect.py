from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation, PanelUi
from modules.page_object import AboutAddons
from modules.util import Utilities

themes = {
    "firefox-compact-dark_mozilla_org-heading": "rgb(43, 42, 51)",
    "firefox-compact-light_mozilla_org-heading": "rgb(249, 249, 251)",
    "firefox-alpenglow_mozilla_org-heading": "rgba(255, 255, 255, 0.76)",
}


@pytest.mark.ci
def test_redirect_to_addons(driver: Firefox):
    """
    C118173, ensures that the user is redirected to about:addons through the ui panel
    """
    panel = PanelUi(driver).open()
    panel.open_panel_menu()
    panel.navigate_to_about_addons()
    windows = driver.window_handles
    driver.switch_to.window(windows[2])
    assert driver.current_url == "about:addons"


@pytest.mark.parametrize("theme_name", list(themes.keys()))
def test_open_addons(driver: Firefox, theme_name: str):
    """
    C118173, continutation ensures that all the themes are set correctly
    """
    nav = Navigation(driver).open()
    abt_addons = AboutAddons(driver).open()
    abt_addons.choose_sidebar_option("theme")
    abt_addons.activate_theme(nav, theme_name, themes[theme_name])
