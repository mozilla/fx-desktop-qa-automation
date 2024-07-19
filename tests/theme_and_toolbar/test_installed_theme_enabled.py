import sys
from os import environ

import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutAddons, AmoThemes

MAC_GHA = environ.get("GITHUB_ACTIONS") and sys.platform.startswith("darwin")


@pytest.mark.skipif(MAC_GHA, reason="Test unstable in MacOS Github Actions")
def test_find_more_themes(driver: Firefox):
    """
    C118174, first part
    """
    about_addons = AboutAddons(driver).open()
    about_addons.choose_sidebar_option("theme")
    about_addons.get_element("find-more-themes-button").click()
    driver.switch_to.window(driver.window_handles[-1])

    # Continuing to call the object "about_addons" is confusing
    base = about_addons
    base.url_contains("addons.mozilla.org")
    base.url_contains("firefox/themes")


@pytest.mark.skipif(MAC_GHA, reason="Test unstable in MacOS Github Actions")
def test_installed_theme_enabled(driver: Firefox):
    """
    C118174: install a theme and make sure it is set to enabled immediately
    """
    about_addons = AboutAddons(driver).open()
    about_addons.choose_sidebar_option("theme")
    starting_theme = about_addons.get_element("enabled-theme-title").get_attribute(
        "innerText"
    )
    amo = AmoThemes(driver).open()
    amo.install_recommended_theme()
    about_addons = AboutAddons(driver).open()
    about_addons.choose_sidebar_option("theme")

    # NOTE: AMO does not enforce that the listed theme name remains the same after installation
    about_addons.check_theme_has_changed(starting_theme)
