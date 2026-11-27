"""
C3310318 - Change the AI model from the Settings page
Verify every AI model offered on the Personalize Smart Window page can be
selected, and that the choice is written through to the backing pref.
"""

import pytest
from auto_fxui.page_object import AboutPrefs
from auto_fxui.page_object_prefs import CUSTOM_MODEL
from selenium.webdriver import Firefox


@pytest.fixture()
def test_case():
    return "3310318"


def test_change_ai_model_from_settings(driver: Firefox):
    """
    C3310318 - Change the AI model from the Settings page
    """
    about_prefs = AboutPrefs(driver, category="ai")
    about_prefs.navigate_to_smart_window_settings()

    models = about_prefs.get_smart_window_models()
    offered = [m["l10n"] for m in models]
    assert CUSTOM_MODEL in offered
    built_in = [m for m in offered if m != CUSTOM_MODEL]
    assert len(built_in) >= 2, f"models offered: {offered}"

    initial = about_prefs.get_smart_window_model()
    assert initial in built_in, f"selected {initial!r} of {offered}"

    for l10n_id in built_in:
        if l10n_id != initial:
            about_prefs.set_smart_window_model(l10n_id)

    # Custom offers fields instead of committing a model; standing one up
    # would need a live LLM endpoint.
    about_prefs.set_smart_window_model(CUSTOM_MODEL)
    about_prefs.element_visible("smart-window-custom-model-name")
    about_prefs.element_visible("smart-window-custom-model-token")

    # Back to the starting model, so the profile is not left on an unusable one.
    about_prefs.set_smart_window_model(initial)
