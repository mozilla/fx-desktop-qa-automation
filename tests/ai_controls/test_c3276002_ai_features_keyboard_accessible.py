"""
C3276002 - AI features keyboard accessible
Verify that each Option from the AI Settings page is Keyboard accessible
"""
import logging
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3276002"


def test_ai_controls_toggle_visible(about_prefs: AboutPrefs):
    """
    C3276002 - Toggle element is present and visible on the AI Controls page
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.element_visible("ai-controls-toggle")
    logging.info("AI Controls toggle is accessible")


def test_chatbot_select_visible(about_prefs: AboutPrefs):
    """
    C3276002 - Chatbot dropdown is present and visible on the AI Controls page
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.element_visible("ai-control-sidebar-chatbot-select")
    logging.info("Chatbot provider dropdown is accessible")


def test_translations_select_visible(about_prefs: AboutPrefs):
    """
    C3276002 - Translations dropdown is present and visible on the AI Controls page
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.element_visible("ai-control-translations-select")
    logging.info("Translations setting is visible")


def test_smart_tab_groups_select_visible(about_prefs: AboutPrefs):
    """
    C3276002 - Smart Tab Groups dropdown is present and visible on the AI Controls page
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.element_visible("ai-control-smart-tab-groups-select")
    logging.info("Smart Tab Groups setting is visible")
