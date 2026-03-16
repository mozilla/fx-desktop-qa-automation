import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi
from modules.page_object import AboutAddons


@pytest.fixture()
def test_case():
    return "118173"


THEMES: dict[str, list[str]] = {
    "firefox-compact-dark_mozilla_org-heading": [
        "rgb(43, 42, 51)",  # classic darker tone
        "rgb(143, 143, 148)",  # focused dark
        "rgb(120, 119, 126)",  # dark without focus
    ],
    # Compact Light
    "firefox-compact-light_mozilla_org-heading": [
        "rgb(249, 249, 251)",
    ],
}

ALPENGLOW_MAP: dict[str, str] = {
    "light": "rgba(255, 255, 255, 0.76)",
    "dark": "rgba(40, 29, 78, 0.96)",
}


def test_redirect_to_addons(driver: Firefox) -> None:
    """
    C118173: Ensure the user is redirected to about:addons via the UI panel.
    """
    panel_ui = PanelUi(driver)
    panel_ui.open()
    panel_ui.open_panel_menu()
    panel_ui.navigate_to_about_addons()

    # remember original window, then switch to newly opened one
    orig = driver.window_handles[0]
    new = driver.window_handles[-1]
    driver.switch_to.window(new)
    assert driver.current_url == "about:addons"

    # cleanup: close the tab we opened and restore focus
    driver.close()
    driver.switch_to.window(orig)


@pytest.mark.parametrize("theme_name", list(THEMES.keys()))
def test_activate_theme_background_matches_expected(
    driver: Firefox, theme_name: str
) -> None:
    """
    C118173: Ensure that activating each theme in about:addons applies the expected
    background color. Handles Developer Edition vs standard Firefox defaults.
    """

    nav = Navigation(driver)
    abt_addons = AboutAddons(driver).open()
    abt_addons.choose_sidebar_option("theme")

    # Dynamically detect if running Developer Edition
    if abt_addons.is_devedition():
        if theme_name == "firefox-compact-dark_mozilla_org-heading":
            pytest.skip("Compact Dark is default on DevEdition, skipping.")
    else:
        if theme_name == "firefox-compact-light_mozilla_org-heading":
            pytest.skip("Compact Light is default on Firefox, skipping.")

    current_bg = abt_addons.activate_theme(nav, theme_name, "", perform_assert=False)

    expected_list = THEMES[theme_name]
    assert any(abt_addons.colors_match(current_bg, exp) for exp in expected_list), (
        f"Got {current_bg} for {theme_name}; expected one of {expected_list}"
    )


def test_alpenglow_theme(driver: Firefox) -> None:
    """
    C118173: Alpenglow theme can render two values depending on light / dark mode.
    Accept either using  the tolerance-based comparison.
    """

    nav = Navigation(driver)
    abt_addons = AboutAddons(driver)
    abt_addons.open()
    abt_addons.choose_sidebar_option("theme")

    current_bg = abt_addons.activate_theme(
        nav, "firefox-alpenglow_mozilla_org-heading", "", perform_assert=False
    )

    assert abt_addons.colors_match(
        current_bg, ALPENGLOW_MAP["light"]
    ) or abt_addons.colors_match(current_bg, ALPENGLOW_MAP["dark"], tolerance=0.18)
