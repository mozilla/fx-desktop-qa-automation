import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import Navigation, PanelUi
from modules.page_base import BasePage
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


class _ChromeProbe:
    """Minimal helper: get a computed style from the chrome context."""

    def __init__(self, driver):
        self.driver = driver

    @BasePage.context_chrome
    def get_main_window_bg(self) -> str:
        return self.driver.execute_script(
            "return window.getComputedStyle("
            "document.getElementById('main-window')"
            ").backgroundColor;"
        )


def _open_private_and_switch(driver: Firefox, panel_ui: PanelUi) -> None:
    """
    Open a private window via the panel and switch the driver to it.

    Note: PanelUi.open_private_window() already calls open_panel_menu()
    internally, so we must not call panel_ui.open() here — doing so would
    toggle the panel and could close it before the item is clicked.
    """
    initial_count = len(driver.window_handles)
    panel_ui.open_private_window()
    WebDriverWait(driver, 15).until(lambda d: len(d.window_handles) > initial_count)
    driver.switch_to.window(driver.window_handles[-1])

    # Sanity: ensure we actually landed in a private window, not a regular one.
    # If PanelUi.open_private_window() regresses and opens a normal window,
    # the color-based assertions alone could still pass.
    assert driver.current_url.startswith("about:privatebrowsing"), (
        f"Expected a private window, got URL {driver.current_url!r}"
    )


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
    """
    Assert that the given private-window background matches one of the known
    dark colors for private windows. Private windows have a distinctive
    background that differs from the main-window COMPACT_DARK palette, so we
    use PRIVATE_WINDOW_DARK with a small tolerance to allow minor platform /
    version drift (e.g. rgb(35, 34, 43) vs rgb(43, 42, 51)).
    """
    expected_list = PRIVATE_WINDOW_DARK
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
    probe = _ChromeProbe(driver)

    original_handle = driver.current_window_handle

    # --- Step 1: Open Private Window and verify dark theme is applied ---
    _open_private_and_switch(driver, panel_ui)

    private_bg = probe.get_main_window_bg()
    _assert_private_window_dark(private_bg, util, "Private Window (default)")

    # Cleanup: close the first private window before moving on
    _close_current_and_back(driver, original_handle)

    # --- Step 2: Change Firefox theme to "Dark" in the original window ---
    about_addons.open()
    about_addons.choose_sidebar_option("theme")
    about_addons.activate_theme(nav, COMPACT_DARK, "", perform_assert=False)

    # Re-open about:addons so the "enabled theme" section reflects the new state.
    # This mirrors the pattern used in test_installed_theme_enabled.py, where
    # the page is re-opened after a theme change.
    about_addons = AboutAddons(driver).open()
    about_addons.choose_sidebar_option("theme")
    _assert_theme_enabled(driver, about_addons, COMPACT_DARK_TITLE)

    # --- Step 3: Open a new Private Window and verify dark theme is still applied ---
    _open_private_and_switch(driver, panel_ui)

    private_bg = probe.get_main_window_bg()
    _assert_private_window_dark(private_bg, util, "Private Window (after Dark theme)")
