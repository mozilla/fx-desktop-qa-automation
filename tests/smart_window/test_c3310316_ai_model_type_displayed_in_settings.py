"""
C3310316 - AI Model Type is displayed in the AI settings page
Verify the Personalize Smart Window page lists every AI model with its name
and description, and marks the configured one as selected.
"""

import pytest
from auto_fxui.page_object import AboutPrefs
from auto_fxui.page_object_prefs import CUSTOM_MODEL
from selenium.webdriver import Firefox


@pytest.fixture()
def test_case():
    return "3310316"


def test_ai_model_type_displayed_in_settings(driver: Firefox):
    """
    C3310316 - AI Model Type is displayed in the AI settings page
    """
    about_prefs = AboutPrefs(driver, category="ai")
    about_prefs.navigate_to_smart_window_settings()

    about_prefs.element_visible("smart-window-model-section")
    models = about_prefs.get_smart_window_models()
    assert CUSTOM_MODEL in [m["l10n"] for m in models]

    built_in = [m for m in models if m["l10n"] != CUSTOM_MODEL]
    assert built_in, "no built-in models offered"
    for model in built_in:
        assert model["label"], f"no name in {model['l10n']}"
        assert model["description"], f"no description in {model['l10n']}"

    choice = about_prefs.get_smart_window_model_choice()
    selected = [m for m in models if m["checked"]]
    assert [m["value"] for m in selected] == [choice], (
        f"selected {[m['l10n'] for m in selected]}, pref is {choice!r}"
    )
