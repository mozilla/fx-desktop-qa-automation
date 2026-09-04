"""
C3309851 - Smart Window option missing in Private Browsing
Verify that a Private Browsing window offers no way to switch to a Smart
Window, while the normal window it was opened from still does.
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.browser_object_smart_window import SmartWindow


@pytest.fixture()
def test_case():
    return "3309851"


def test_smart_window_missing_in_private_browsing(
    driver: Firefox, smart_window: SmartWindow
):
    """
    C3309851 - Smart Window option missing in Private Browsing
    """
    # Baseline: the normal window offers the Smart option.
    assert smart_window.switcher_button_available()
    smart_window.open_window_switcher()
    smart_window.element_visible("switch-to-smart")
    smart_window.close_window_switcher()

    panel_ui = PanelUi(driver)
    existing_handles = set(driver.window_handles)
    panel_ui.open_private_window()
    driver.switch_to.window(smart_window.wait_for_new_window(existing_handles))

    private_window = SmartWindow(driver)
    private_window.is_private()  # waits and asserts; raises on timeout

    # The Switch Windows button is not built at all in a private window, so
    # there is no entry point to a Smart Window.
    assert not private_window.switcher_button_available()
