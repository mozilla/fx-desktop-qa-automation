"""
C3311329 - Open/Close the AI chat from the ASK button
Verify that the Ask button in the toolbar opens the Assistant chat sidebar and
closes it again when clicked a second time.
"""

import pytest

from modules.browser_object import SmartWindow


@pytest.fixture()
def test_case():
    return "3311329"


def test_toggle_ai_chat_from_ask_button(active_smart_window: SmartWindow):
    """
    C3311329 - Open/Close the AI chat from the ASK button
    """
    smart_window = active_smart_window

    # The sidebar starts closed in a freshly activated Smart Window. Assert
    # that structural precondition first, then the button that acts on it.
    smart_window.expect_ai_sidebar_open(False)
    smart_window.element_visible("smart-window-ask-button")

    smart_window.toggle_ai_sidebar()
    smart_window.expect_ai_sidebar_open(True)

    # A second click on the same button closes it.
    smart_window.toggle_ai_sidebar()
    smart_window.expect_ai_sidebar_open(False)
