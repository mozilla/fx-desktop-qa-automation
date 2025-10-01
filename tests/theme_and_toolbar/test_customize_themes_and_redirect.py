import pytest
from selenium.webdriver import Firefox
from modules.browser_object import Navigation, PanelUi
from modules.page_object import AboutAddons


@pytest.fixture()
def test_case():
    return "118173"


# Exact values preserved from the original file
THEMES: dict[str, str] = {
    "firefox-compact-dark_mozilla_org-heading": "rgb(43, 42, 51)",
    "firefox-compact-light_mozilla_org-heading": "rgb(249, 249, 251)",
}

ALPENGLOW_MAP: dict[str, str] = {
    "light": "rgba(255, 255, 255, 0.76)",
    "dark": "rgba(40, 29, 78, 0.96)",
}


def colors_match(a: str, b: str, tolerance: float = 0.14) -> bool:
    """
    Determine if two CSS colors are close enough to be considered matches.
    Preserves the original multiplicative tolerance logic and supports rgb/rgba.
    """
    try:
        a_vals = a.split("(")[1][:-1]
        b_vals = b.split("(")[1][:-1]
        a_nums = [float(n.strip()) for n in a_vals.split(",")]
        b_nums = [float(n.strip()) for n in b_vals.split(",")]
        for i in range(min(len(a_nums), len(b_nums))):
            base = b_nums[i] if b_nums[i] != 0 else 1.0  # avoid div by zero
            diff = abs((a_nums[i] / base) - 1.0)
            if diff > tolerance:
                return False
        return True
    except Exception:
        return False


@pytest.mark.ci
def test_redirect_to_addons(driver: Firefox) -> None:
    """
    C118173: ensure the user is redirected to about:addons through the UI panel.
    """
    panel_ui = PanelUi(driver)
    panel_ui.open()
    panel_ui.open_panel_menu()
    panel_ui.navigate_to_about_addons()
    windows = driver.window_handles
    driver.switch_to.window(windows[2])
    assert driver.current_url == "about:addons"


@pytest.mark.parametrize("theme_name", list(THEMES.keys()))
def test_open_addons(driver: Firefox, theme_name: str) -> None:
    """
    C118173: continuation ensures that all the themes are set correctly.
    Handles Developer Edition vs standard Firefox defaults as in the original.
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

    current_bg = abt_addons.activate_theme(
        nav, theme_name, THEMES[theme_name], perform_assert=False
    )
    assert colors_match(current_bg, THEMES[theme_name])


def test_alpenglow_theme(driver: Firefox) -> None:
    """
    C118173: Alpenglow theme can render two values depending on light/dark mode.
    Accept either using the tolerance-based comparison.
    """
    nav = Navigation(driver)
    abt_addons = AboutAddons(driver).open()
    abt_addons.choose_sidebar_option("theme")

    current_bg = abt_addons.activate_theme(
        nav, "firefox-alpenglow_mozilla_org-heading", "", perform_assert=False
    )

    assert colors_match(current_bg, ALPENGLOW_MAP["light"]) or colors_match(
        current_bg, ALPENGLOW_MAP["dark"]
    )
