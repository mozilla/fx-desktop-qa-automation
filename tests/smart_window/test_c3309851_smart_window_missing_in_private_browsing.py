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
    smart_window.element_visible("window-switcher-button")
    smart_window.open_window_switcher()
    smart_window.element_visible("switch-to-smart")
    smart_window.close_window_switcher()

    panel_ui = PanelUi(driver)
    existing_count = len(driver.window_handles)
    panel_ui.open_private_window()
    smart_window.wait_for_num_windows(existing_count + 1)
    smart_window.switch_to_new_window()

    private_window = SmartWindow(driver)
    private_window.is_private()

    # No Switch Windows button in a private window: entry point never built.
    private_window.element_does_not_exist("window-switcher-button")
