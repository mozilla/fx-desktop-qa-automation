from platform import system

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi
from modules.page_object import AboutAddons


@pytest.fixture()
def test_case():
    return "118173"


themes = {
    "firefox-compact-dark_mozilla_org-heading": "rgb(43, 42, 51)",
    "firefox-compact-light_mozilla_org-heading": "rgb(249, 249, 251)",
}

alpenglow_map = {"light": "rgba(255, 255, 255, 0.76)", "dark": "rgba(40, 29, 78, 0.96)"}


@pytest.mark.ci
def test_redirect_to_addons(driver: Firefox):
    """
    C118173, ensures that the user is redirected to about:addons through the ui panel
    """
    panel_ui = PanelUi(driver)
    panel_ui.open()
    panel_ui.open_panel_menu()
    panel_ui.navigate_to_about_addons()
    windows = driver.window_handles
    driver.switch_to.window(windows[2])
    assert driver.current_url == "about:addons"


@pytest.mark.skipif(system().lower().startswith("win"), reason="Bug 1974109")
@pytest.mark.parametrize("theme_name", list(themes.keys()))
def test_open_addons(driver: Firefox, theme_name: str):
    """
    C118173, continuation ensures that all the themes are set correctly
    """
    nav = Navigation(driver)
    abt_addons = AboutAddons(driver).open()
    abt_addons.choose_sidebar_option("theme")

    # Dynamically detect if running Developer Edition
    if abt_addons.is_devedition():
        # Adjust expectations for Developer Edition
        if theme_name == "firefox-compact-dark_mozilla_org-heading":
            # Already default on Developer Edition; skip activation/assertion
            pytest.skip("Compact Dark is default on DevEdition, skipping.")
    else:
        # Adjust expectations for standard Firefox
        if theme_name == "firefox-compact-light_mozilla_org-heading":
            # Already default on Firefox standard; skip activation/assertion
            pytest.skip("Compact Light is default on Firefox, skipping.")

    abt_addons.activate_theme(nav, theme_name, themes[theme_name])


@pytest.mark.skipif(system().lower().startswith("win"), reason="Bug 1974109")
def test_alpenglow_theme(driver: Firefox):
    """
    C118173, specifically for alpenglow theme because color can be two values for dark or light mode
    """

    nav = Navigation(driver)
    abt_addons = AboutAddons(driver).open()
    abt_addons.choose_sidebar_option("theme")
    current_bg = abt_addons.activate_theme(
        nav, "firefox-alpenglow_mozilla_org-heading", "", perform_assert=False
    )

    assert current_bg == alpenglow_map["light"] or current_bg == alpenglow_map["dark"]
