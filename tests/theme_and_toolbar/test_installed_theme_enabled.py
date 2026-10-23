from urllib.parse import urlsplit

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from modules.page_object import AboutAddons, AmoThemes
from modules.theme_constants import AMO_HOST, AMO_THEMES_PATH


@pytest.fixture()
def test_case():
    return "118174"


WAIT_TIMEOUT = 30


# Test is unstable in MacOS GHA for now
def test_find_more_themes(driver: Firefox) -> None:
    """
    From about:addons > Themes, 'Find more themes' opens AMO in a new tab.
    """
    about_addons = AboutAddons(driver).open()
    about_addons.choose_sidebar_option("theme")

    original_handle = driver.current_window_handle
    original_handles = set(driver.window_handles)
    new_handle = None

    try:
        about_addons.click_find_more_themes()

        wait = WebDriverWait(driver, WAIT_TIMEOUT)
        wait.until(
            EC.new_window_is_opened(original_handles),
            message="'Find more themes' did not open a new tab",
        )

        new_handles = set(driver.window_handles) - original_handles
        assert len(new_handles) == 1, f"Expected one new tab, found {len(new_handles)}"

        new_handle = new_handles.pop()
        driver.switch_to.window(new_handle)

        def amo_themes_loaded(browser: Firefox) -> bool:
            url = urlsplit(browser.current_url)
            return url.hostname == AMO_HOST and url.path.rstrip("/").endswith(
                AMO_THEMES_PATH
            )

        wait.until(
            amo_themes_loaded,
            message="The new tab did not navigate to the AMO themes page",
        )
    finally:
        handles = driver.window_handles

        if new_handle is not None and new_handle in handles:
            driver.switch_to.window(new_handle)
            driver.close()

        if original_handle in driver.window_handles:
            driver.switch_to.window(original_handle)


def test_installed_theme_enabled(driver: Firefox) -> None:
    """
    Install a recommended theme from AMO and ensure it becomes enabled immediately.
    """
    about_addons = AboutAddons(driver).open()
    about_addons.choose_sidebar_option("theme")

    # Capture currently enabled theme title
    starting_theme = about_addons.get_element("enabled-theme-title").get_attribute(
        "innerText"
    )

    # Go to AMO and install a recommended theme (POM encapsulates waits and flows)
    amo_themes = AmoThemes(driver).open()
    amo_themes.install_recommended_theme()
    amo_themes.confirm_addon_install_popup()

    # Return to about:addons > Themes and verify the enabled theme changed
    about_addons = AboutAddons(driver).open()
    about_addons.choose_sidebar_option("theme")

    # AMO may change display names; we only assert that the enabled theme is different
    about_addons.check_theme_has_changed(starting_theme)
