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
    "firefox-alpenglow_mozilla_org-heading": "rgba(40, 29, 78, 0.96)",
}


def test_redirect_to_addons(driver: Firefox):
    panel = PanelUi(driver).open()

    panel.open_panel_menu()
    panel.navigate_to_about_addons()
    windows = driver.window_handles
    driver.switch_to.window(windows[2])
    assert driver.current_url == "about:addons"


@pytest.mark.parametrize("theme_name", list(themes.keys()))
def test_open_addons(driver: Firefox, theme_name):
    nav = Navigation(driver).open()
    abt_addons = AboutAddons(driver).open()
    abt_addons.choose_sidebar_option("theme")
    abt_addons.activate_theme(nav, theme_name, themes[theme_name])
