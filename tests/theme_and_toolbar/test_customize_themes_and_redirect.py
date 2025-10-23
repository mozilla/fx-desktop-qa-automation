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


def colors_match(a: str, b: str, tolerance: float = 0.14) -> bool:
    """
    Compare two CSS color strings and determine if they are close enough to be considered equal.

    Args:
        a (str): First CSS color string in 'rgb(r,g,b)' or 'rgba(r,g,b,a)' format.
        b (str): Second CSS color string in 'rgb(r,g,b)' or 'rgba(r,g,b,a)' format.
        tolerance (float, optional): Allowed relative difference between each color channel.
            Defaults to 0.14. A higher value means colors can differ more and still match.

    Returns:
        bool: True if the two colors are considered a match within the given tolerance.
              False if the color strings are invalid.
    """
    try:
        a_vals = a.split("(")[1][:-1]
        b_vals = b.split("(")[1][:-1]
        a_nums = [float(n.strip()) for n in a_vals.split(",")]
        b_nums = [float(n.strip()) for n in b_vals.split(",")]
    except (IndexError, ValueError):
        # Raised if string doesn't contain expected format or non-numeric parts
        return False

    # Compare up to the shortest length (rgb vs rgba)
    for i in range(min(len(a_nums), len(b_nums))):
        base = b_nums[i] if b_nums[i] != 0 else 1.0
        diff = abs((a_nums[i] / base) - 1.0)
        if diff > tolerance:
            return False

    return True


@pytest.mark.ci
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
    C118173: Ensure that activating each theme in about:addons applies the expected background color.
    Handles Developer Edition vs standard Firefox defaults.
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
    assert any(colors_match(current_bg, exp) for exp in expected_list), (
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

    assert colors_match(current_bg, ALPENGLOW_MAP["light"]) or colors_match(
        current_bg, ALPENGLOW_MAP["dark"]
    )
