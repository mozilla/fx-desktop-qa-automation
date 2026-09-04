"""
C3310319 - Enable/Block Smart Window from AI controls
Verify that blocking Smart Window in AI Controls removes the Switch Windows
button, and that unblocking it brings the button back.
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_smart_window import SmartWindow
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3310319"


def test_block_smart_window_from_ai_controls(driver: Firefox):
    """
    C3310319 - Enable/Block Smart Window from AI controls
    """
    smart_window = SmartWindow(driver)
    about_prefs = AboutPrefs(driver, category="ai")
    about_prefs.navigate_to_ai_controls()

    # The feature starts available, so the window switcher is offered.
    assert about_prefs.get_ai_smart_window_state() == "available"
    assert smart_window.switcher_button_available()

    about_prefs.set_ai_smart_window("blocked")
    smart_window.expect(lambda _: not smart_window.switcher_button_available())

    about_prefs.set_ai_smart_window("available")
    smart_window.expect(lambda _: smart_window.switcher_button_available())
