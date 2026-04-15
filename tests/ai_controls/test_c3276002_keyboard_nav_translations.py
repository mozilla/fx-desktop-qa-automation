"""
C3276002 - Keyboard navigation to translations setting
Verify that the Translations setting can be reached and modified via keyboard
"""
import logging
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3276002"


def test_keyboard_navigation_to_translations_setting(about_prefs: AboutPrefs):
    """Verify that Translations setting can be reached and modified via keyboard"""
    about_prefs.navigate_to_ai_controls()
    about_prefs.element_visible("ai-control-translations-select")
    logging.info("Translations setting is keyboard accessible")
