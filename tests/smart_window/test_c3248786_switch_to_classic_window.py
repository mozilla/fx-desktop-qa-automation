"""
C3248786 - Switch to Classic Window from the Switch Windows button
Verify a Smart Window can be turned back into a Classic Window from the Switch
Windows panel, and that the Smart Window chrome is torn down with it.
"""

import pytest

from modules.browser_object_smart_window import SmartWindow


@pytest.fixture()
def test_case():
    return "3248786"


def test_switch_to_classic_window(active_smart_window: SmartWindow):
    """
    C3248786 - Switch to Classic Window from the Switch Windows button
    """
    smart_window = active_smart_window

    # The switcher reflects the window it is opened from.
    smart_window.open_window_switcher()
    smart_window.expect_switcher_selection("smart")
    smart_window.close_window_switcher()

    smart_window.element_visible("smart-window-ask-button")

    smart_window.switch_to_classic_window()

    # Smart Window chrome is gone once the window is Classic again.
    smart_window.element_not_visible("smart-window-ask-button")
    smart_window.open_window_switcher()
    smart_window.expect_switcher_selection("classic")
