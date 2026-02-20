import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation


@pytest.fixture()
def test_case():
    return "101661"


def test_open_private_browsing_via_keyboard(driver: Firefox):
    """
    C101661: Verify that a Private Browsing session can be opened via keyboard shortcut (Ctrl+Shift+P on
    Windows/Linux, Cmd+Shift+P on macOS) and the purple mask is displayed.
    """
    # Instantiate objects
    nav = Navigation(driver)

    # Open a new private browsing window via keyboard shortcut and switch to it
    nav.open_and_switch_to_private_window_via_keyboard()

    # Verify the Private Browsing window is opened
    nav.is_private()

    # Verify the purple mask (private browsing indicator icon) is displayed
    nav.element_visible("private-browsing-icon")
