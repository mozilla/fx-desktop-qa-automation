import pytest
from selenium.webdriver import Firefox

from auto_fxui.browser_object import Navigation
from auto_fxui.page_object import AboutAddons

WIKIPEDIA_URL = "https://www.wikipedia.org/"
DARK_CARD = "firefox-compact-dark_mozilla_org-heading"
LIGHT_CARD = "firefox-compact-light_mozilla_org-heading"
DARK_THEME_ID = "firefox-compact-dark@mozilla.org"
LIGHT_THEME_ID = "firefox-compact-light@mozilla.org"


@pytest.fixture()
def test_case():
    return "3814265"


def test_theme_reflected_in_taskbar_tab(driver: Firefox):
    """
    C3814265 - Verify that themes applied to the main instance are reflected in all Taskbar Tabs windows
    """

    # Instantiate objects
    nav = Navigation(driver)
    about_addons = AboutAddons(driver)

    # Set the browser theme to Dark
    about_addons.open()
    about_addons.choose_sidebar_option("theme")
    about_addons.activate_theme(nav, DARK_CARD, "", perform_assert=False)
    main_handle = driver.current_window_handle

    # Open Wikipedia in a new tab and move it into a Taskbar Tabs window
    nav.open_and_switch_to_new_window("tab")
    driver.get(WIKIPEDIA_URL)
    nav.click_on("taskbar-tabs-button")
    nav.wait_for_taskbar_tab_window()
    taskbar_handle = driver.current_window_handle

    # The Taskbar Tabs window has the Dark theme too
    nav.wait_for_taskbar_tab_theme(DARK_THEME_ID)

    # Switch the main window to the Light theme
    driver.switch_to.window(main_handle)
    about_addons.choose_sidebar_option("theme")
    about_addons.activate_theme(nav, LIGHT_CARD, "", perform_assert=False)
    driver.switch_to.window(taskbar_handle)

    # The Taskbar Tabs window follows the change to Light
    nav.wait_for_taskbar_tab_theme(LIGHT_THEME_ID)
