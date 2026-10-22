"""
C3310316 - AI Model Type is displayed in the AI settings page
Verify the Personalize Smart Window page lists every AI model with its name,
type and description, and marks the configured one as selected.
"""

import re

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import SmartWindow
from modules.page_object import AboutPrefs

# The model the suite's prefs_list selects (modelChoice "1").
EXPECTED_MODEL = "smart-window-model-fast-v2"

# Each label reads "<model name>: <type>", e.g. "Gemini 3.1 Flash Lite: Fast".
LABEL = re.compile(r"^.+: .+$")


@pytest.fixture()
def test_case():
    return "3310316"


def test_ai_model_type_displayed_in_settings(
    driver: Firefox, smart_window: SmartWindow
):
    """
    C3310316 - AI Model Type is displayed in the AI settings page
    """
    about_prefs = AboutPrefs(driver, category="ai")
    about_prefs.navigate_to_smart_window_settings()

    about_prefs.element_visible("smart-window-model-section")
    models = about_prefs.get_smart_window_models()

    # Four choices are offered: three built-in models plus Custom.
    assert len(models) == 4, f"expected 4 models, got {[m['l10n'] for m in models]}"

    built_in = [m for m in models if m["l10n"] != "smart-window-model-custom"]
    for model in built_in:
        # "<name>: <type>" in the label, and the full model id in the blurb.
        assert LABEL.match(model["label"] or ""), f"no name/type in {model['label']!r}"
        assert "Full name:" in (model["description"] or ""), (
            f"no model id in {model['l10n']} description: {model['description']!r}"
        )

    about_prefs.expect_smart_window_model(EXPECTED_MODEL)
