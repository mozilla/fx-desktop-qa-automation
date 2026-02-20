import platform

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_menu_bar import MenuBar
from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi


@pytest.fixture()
def test_case():
    return "2359316"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.privatebrowsing.resetPBM.enabled", True),
        ("browser.privatebrowsing.felt-privacy-v1", True),
    ]


def test_sidebar_removed_on_end_private_session(driver: Firefox):
    """
    C2359316 - Verify that the Sidebar is removed when "End Private Session" is used in a Private Window
    """
    # Instantiate objects
    nav = Navigation(driver)
    panel = PanelUi(driver)
    menu_bar = MenuBar(driver)

    # Open a private window and switch to it
    panel.open_and_switch_to_new_window("private")

    # Activate the Sidebar via menu bar (native on macOS, not supported)
    if platform.system() == "Darwin":
        pytest.skip("View menu bar sidebar navigation is not supported on macOS")
    menu_bar.open_sidebar_panel_from_menu_bar("History")

    # Verify the sidebar is open
    nav.element_visible("sidebar-box")

    # Click "End Private Session" and confirm "Delete session data"
    nav.end_private_session()

    # Verify the sidebar is closed
    nav.element_not_visible("sidebar-box")
