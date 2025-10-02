import sys
from os import environ

import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutAddons, AmoThemes


@pytest.fixture()
def test_case():
    return "118174"


MAC_GHA: bool = environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("darwin")

AMO_HOST: str = "addons.mozilla.org"
AMO_THEMES_PATH: str = "firefox/themes"


@pytest.mark.skipif(MAC_GHA, reason="Test unstable in MacOS Github Actions")
def test_find_more_themes(driver: Firefox) -> None:
    """
    C118174 (part 1): From about:addons > Themes, 'Find more themes' opens AMO in a new tab.
    Verify AMO host and themes path are present in the URL.
    """
    about_addons = AboutAddons(driver).open()
    about_addons.choose_sidebar_option("theme")
    about_addons.get_element("find-more-themes-button").click()

    driver.switch_to.window(driver.window_handles[-1])

    base = about_addons
    base.url_contains(AMO_HOST)
    base.url_contains(AMO_THEMES_PATH)


@pytest.mark.skipif(MAC_GHA, reason="Test unstable in MacOS Github Actions")
def test_installed_theme_enabled(driver: Firefox) -> None:
    """
    C118174 (part 2): Install a recommended theme from AMO and ensure it becomes enabled immediately.
    """
    about_addons = AboutAddons(driver).open()
    about_addons.choose_sidebar_option("theme")

    # Capture currently enabled theme title
    starting_theme = about_addons.get_element("enabled-theme-title").get_attribute("innerText")

    # Go to AMO and install a recommended theme (POM encapsulates waits and flows)
    AmoThemes(driver).open().install_recommended_theme()

    # Return to about:addons > Themes and verify the enabled theme changed
    about_addons = AboutAddons(driver).open()
    about_addons.choose_sidebar_option("theme")

    # AMO may change display names; we only assert that the enabled theme is different
    about_addons.check_theme_has_changed(starting_theme)
