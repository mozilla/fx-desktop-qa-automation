"""
C3310319 - Enable/Block Smart Window from AI controls
Verify that blocking Smart Window in AI Controls removes the Switch Windows
button, and that unblocking it brings the button back.
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import SmartWindow
from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "3310319"


def test_block_smart_window_from_ai_controls(
    driver: Firefox, smart_window: SmartWindow
):
    """
    C3310319 - Enable/Block Smart Window from AI controls
    """
    about_prefs = AboutPrefs(driver, category="ai")
    about_prefs.navigate_to_ai_controls()

    # The feature starts available, so the window switcher is offered.
    about_prefs.expect_ai_smart_window_state("available")
    smart_window.element_visible("window-switcher-button")

    about_prefs.set_ai_smart_window("blocked")
    smart_window.element_does_not_exist("window-switcher-button")

    about_prefs.set_ai_smart_window("available")
    smart_window.element_visible("window-switcher-button")
