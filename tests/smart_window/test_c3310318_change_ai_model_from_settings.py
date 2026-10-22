"""
C3310318 - Change the AI model from the Settings page
Verify every AI model offered on the Personalize Smart Window page can be
selected, and that the choice is written through to the backing pref.
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import SmartWindow
from modules.page_object import AboutPrefs

FAST = "smart-window-model-fast-v2"
FLEXIBLE = "smart-window-model-flexible-v2"
PERSONAL = "smart-window-model-personal-v2"
CUSTOM = "smart-window-model-custom"


@pytest.fixture()
def test_case():
    return "3310318"


def test_change_ai_model_from_settings(driver: Firefox, smart_window: SmartWindow):
    """
    C3310318 - Change the AI model from the Settings page
    """
    about_prefs = AboutPrefs(driver, category="ai")
    about_prefs.navigate_to_smart_window_settings()

    # All four choices are offered, and the suite's pref selects Fast.
    offered = {m["l10n"] for m in about_prefs.get_smart_window_models()}
    assert offered == {FAST, FLEXIBLE, PERSONAL, CUSTOM}, f"models offered: {offered}"
    about_prefs.expect_smart_window_model(FAST)

    # Each built-in model can be selected, and writes through to the pref.
    about_prefs.set_smart_window_model(FLEXIBLE)
    about_prefs.set_smart_window_model(PERSONAL)

    # Custom offers its own fields instead of committing a model. Standing one
    # up would need a live LLM endpoint, so this asserts the fields are offered,
    # which is what "users are free to set up a custom AI model" can mean here.
    about_prefs.set_smart_window_model(CUSTOM)
    about_prefs.element_visible("smart-window-custom-model-name")
    about_prefs.element_visible("smart-window-custom-model-token")

    # Back to the suite default, so the choice is not left on an unusable model.
    about_prefs.set_smart_window_model(FAST)
