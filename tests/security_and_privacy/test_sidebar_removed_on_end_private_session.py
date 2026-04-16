import platform

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation, PanelUi


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
    driver: Firefox, nav: Navigation, panel_ui: PanelUi
):
    """
    C2359316 - Verify that the Sidebar is removed when "End Private Session"
    is used in a Private Window
    """
    # Open a private window and switch to it
    panel_ui.open_and_switch_to_new_window("private")

    # Activate the Sidebar via hotkey
    if platform.system() == "Darwin":
        nav.perform_key_combo_chrome(Keys.SHIFT, Keys.COMMAND, "h")
    else:
        nav.perform_key_combo_chrome(Keys.SHIFT, Keys.CONTROL, "h")

    # Verify the sidebar is open
    nav.element_visible("sidebar-box")

    # Click "End Private Session" and confirm "Delete session data"
    nav.end_private_session()

    # Verify the sidebar is closed
    nav.element_not_visible("sidebar-box")
