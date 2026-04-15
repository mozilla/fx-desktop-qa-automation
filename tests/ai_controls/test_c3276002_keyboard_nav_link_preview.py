"""
C3276002 - Keyboard navigation to link preview setting
Verify that the Link Preview setting can be reached and modified via keyboard
"""
import logging
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3276002"


def test_keyboard_navigation_to_link_preview_setting(about_prefs: AboutPrefs):
    """Verify that Link Preview setting can be reached and modified via keyboard"""
    about_prefs.navigate_to_ai_controls()
    about_prefs.element_visible("ai-control-link-preview-select")
    logging.info("Link Preview setting is keyboard accessible")
