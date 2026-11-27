"""
C3917535 - The Smart Window can be blocked via policies
"""

import pytest
from auto_fxui.browser_object import PanelUi, SmartWindow
from auto_fxui.page_object import AboutPrefs, SmartWindowFirstRun
from selenium.webdriver import Firefox

SMART_WINDOW_PREF = "browser.smartwindow.enabled"


@pytest.fixture()
def test_case():
    return "3917535"


@pytest.fixture()
def enterprise_policies():
    return {"GenerativeAI": {"SmartWindow": False, "Locked": True}}


@pytest.fixture()
def fxa_env():
    return None


def test_block_smart_window_by_policy(driver: Firefox, smart_window: SmartWindow):
    """
    C3917535 - The Smart Window can be blocked via policies
    """
    prefs = SmartWindowFirstRun(driver)
    assert prefs.get_pref(SMART_WINDOW_PREF) is False
    assert prefs.is_pref_locked(SMART_WINDOW_PREF)

    smart_window.element_does_not_exist("window-switcher-button")
    panel_ui = PanelUi(driver)
    panel_ui.open_panel_menu()
    panel_ui.element_not_visible("panel-ui-new-smart-window")

    about_prefs = AboutPrefs(driver, category="ai")
    about_prefs.navigate_to_ai_controls(verify=False)
    about_prefs.expect_ai_smart_window_state("blocked")
    about_prefs.element_has_attribute("ai-control-smart-window-select", "disabled")
