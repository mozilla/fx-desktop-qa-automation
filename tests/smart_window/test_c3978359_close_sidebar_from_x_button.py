"""
C3978359 - Close the Sidebar from the X Close button
Verify that the Assistant chat sidebar can be dismissed with its own X button.
"""

import pytest

from modules.browser_object import SmartWindow


@pytest.fixture()
def test_case():
    return "3978359"


def test_close_sidebar_from_x_button(active_smart_window: SmartWindow):
    """
    C3978359 - Close the Sidebar from the X Close button
    """
    smart_window = active_smart_window

    smart_window.toggle_ai_sidebar()
    smart_window.expect_ai_sidebar_open(True)

    smart_window.close_ai_sidebar()
    smart_window.expect_ai_sidebar_open(False)
