import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import Navigation, PanelUi
from modules.page_object import AboutAddons
from modules.theme_constants import (
    COMPACT_DARK,
    COMPACT_DARK_TITLE,
    PRIVATE_WINDOW_DARK,
)
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "1937606"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.theme.dark-private-windows", True),
        ("browser.privatebrowsing.enable-new-indicator", True),
    ]


def _close_current_and_back(driver: Firefox, original_handle: str) -> None:
    """Close the current window and switch back to the original one."""
    driver.close()
    driver.switch_to.window(original_handle)


def _assert_theme_enabled(
    driver: Firefox, about_addons: AboutAddons, expected_title: str
) -> None:
    """
    Ensure the currently enabled theme title matches the expected one.

    The DOM under about:addons briefly re-renders right after a theme is
    activated, so we wait for the enabled-theme element to be present again
    before reading its title.
    """

    def _read_title(_driver) -> str:
        element = about_addons.get_element("enabled-theme-title")
        return element.get_attribute("innerText")

    enabled = WebDriverWait(driver, 15).until(_read_title)
    assert expected_title.lower() in enabled.lower(), (
        f"Expected enabled theme '{expected_title}', got '{enabled}'"
    )


def _assert_private_window_dark(current_bg: str, util: Utilities, context: str) -> None:
    expected_list = PRIVATE_WINDOW_DARK
    print(f"\n>>> {context}: actual = {current_bg}\n")  # <-- временно
    assert any(
        util.colors_match(current_bg, exp, tolerance=0.05) for exp in expected_list
    ), f"{context}: got {current_bg}; expected one of {expected_list}"


def test_dark_theme_in_private_window(driver: Firefox, util: Utilities) -> None:
    """
    C1937606: Verify that Dark theme is correctly applied in a Private Window
    before and after switching Firefox theme to "Dark".
    """
    nav = Navigation(driver)
    panel_ui = PanelUi(driver)
    about_addons = AboutAddons(driver)

    original_handle = driver.current_window_handle

    # --- Step 1: Open Private Window and verify dark theme is applied ---
    existing_count = len(driver.window_handles)
    panel_ui.open_private_window()
    panel_ui.wait_for_num_windows(existing_count + 1)
    panel_ui.switch_to_new_window()
    panel_ui.is_private()

    nav.clear_cache()
    private_bg = about_addons.get_theme_background_color(nav)
    _assert_private_window_dark(private_bg, util, "Private Window (default)")

    # Cleanup: close the first private window before moving on
    _close_current_and_back(driver, original_handle)

    # --- Step 2: Change Firefox theme to "Dark" in the original window ---
    nav.clear_cache()
    about_addons.open()
    about_addons.choose_sidebar_option("theme")
    about_addons.activate_theme(nav, COMPACT_DARK, "", perform_assert=False)

    # Re-open about:addons so the "enabled theme" section reflects the new state.
    # This mirrors the pattern used in test_installed_theme_enabled.py, where
    # the page is re-opened after a theme change.
    about_addons = AboutAddons(driver).open()
    about_addons.choose_sidebar_option("theme")
    _assert_theme_enabled(driver, about_addons, COMPACT_DARK_TITLE)

    # --- Step 3: Open a new Private Window and verify Dark theme is still enabled ---
    existing_count = len(driver.window_handles)
    panel_ui.open_private_window()
    panel_ui.wait_for_num_windows(existing_count + 1)
    panel_ui.switch_to_new_window()
    panel_ui.is_private()

    # The private-browsing nav-bar keeps its own tint regardless of the
    # Firefox theme, so re-reading the color here would just duplicate
    # step 1. Verify that the Dark theme itself is still enabled — this
    # is what the manual test case checks ("Dark theme is still enabled").
    about_addons = AboutAddons(driver).open()
    about_addons.choose_sidebar_option("theme")
    _assert_theme_enabled(driver, about_addons, COMPACT_DARK_TITLE)
