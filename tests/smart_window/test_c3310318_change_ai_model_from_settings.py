"""
C3310318 - Change the AI model from the Settings page
Verify every AI model offered on the Personalize Smart Window page can be
selected, and that the choice is written through to the backing pref.
"""

import pytest
from auto_fxui.page_object import AboutPrefs
from auto_fxui.page_object_prefs import CUSTOM_MODEL
from selenium.webdriver import Firefox

FAST = "smart-window-model-fast-v2"
FLEXIBLE = "smart-window-model-flexible-v2"
PERSONAL = "smart-window-model-personal-v2"


@pytest.fixture()
def test_case():
    return "3310318"


def test_change_ai_model_from_settings(driver: Firefox):
    """
    C3310318 - Change the AI model from the Settings page
    """
    about_prefs = AboutPrefs(driver, category="ai")
    about_prefs.navigate_to_smart_window_settings()

    offered = {m["l10n"] for m in about_prefs.get_smart_window_models()}
    assert offered == {FAST, FLEXIBLE, PERSONAL, CUSTOM_MODEL}, (
        f"models offered: {offered}"
    )
    about_prefs.expect_smart_window_model(FAST)

    about_prefs.set_smart_window_model(FLEXIBLE)
    about_prefs.set_smart_window_model(PERSONAL)

    # Custom offers fields instead of committing a model; standing one up
    # would need a live LLM endpoint.
    about_prefs.set_smart_window_model(CUSTOM_MODEL)
    about_prefs.element_visible("smart-window-custom-model-name")
    about_prefs.element_visible("smart-window-custom-model-token")

    # Back to the default, so the profile is not left on an unusable model.
    about_prefs.set_smart_window_model(FAST)
