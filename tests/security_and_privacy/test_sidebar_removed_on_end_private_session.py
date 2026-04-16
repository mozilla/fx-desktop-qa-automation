import platform

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import MenuBar, Navigation, PanelUi


@pytest.fixture()
def test_case():
    return "2359316"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.privatebrowsing.resetPBM.enabled", True),
        ("browser.privatebrowsing.felt-privacy-v1", True),
    ]


def test_sidebar_removed_on_end_private_session(
    driver: Firefox, menu_bar: MenuBar, nav: Navigation, panel_ui: PanelUi
):
    """
    C2359316 - Verify that the Sidebar is removed when "End Private Session"
    is used in a Private Window
    """
    # Open a private window and switch to it
    panel_ui.open_and_switch_to_new_window("private")

    # Activate the Sidebar via menu bar (or hotkey on Mac)
    if platform.system() == "Darwin":
        nav.perform_key_combo_chrome(Keys.SHIFT, Keys.COMMAND, "h")
    else:
        menu_bar.open_sidebar_panel_from_menu_bar("History")

    # Verify the sidebar is open
    nav.element_visible("sidebar-box")

    # Click "End Private Session" and confirm "Delete session data"
    nav.end_private_session()

    # Verify the sidebar is closed
    nav.element_not_visible("sidebar-box")
