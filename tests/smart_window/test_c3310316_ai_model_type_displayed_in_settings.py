"""
C3310316 - AI Model Type is displayed in the AI settings page
Verify the Personalize Smart Window page lists every AI model with its name,
type and description, and marks the configured one as selected.
"""

import re

import pytest
from auto_fxui.page_object import AboutPrefs
from selenium.webdriver import Firefox

# The model prefs_list selects (modelChoice "1").
EXPECTED_MODEL = "smart-window-model-fast-v2"

# Labels read "<name>: <type>", e.g. "Gemini 3.1 Flash Lite: Fast".
LABEL = re.compile(r"^.+: .+$")

# A model id such as gemini-3.1-flash-lite or mistral-small-2603.
MODEL_ID = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+){2,}")


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

    assert len(models) == 4, f"expected 4 models, got {[m['l10n'] for m in models]}"

    built_in = [m for m in models if m["l10n"] != "smart-window-model-custom"]
    for model in built_in:
        assert LABEL.match(model["label"] or ""), f"no name/type in {model['label']!r}"
        # The id itself, not the "Full name:" label, which is localised.
        assert MODEL_ID.search(model["description"] or ""), (
            f"no model id in {model['l10n']} description: {model['description']!r}"
        )

    about_prefs.expect_smart_window_model(EXPECTED_MODEL)
