"""
C3341236 - Chatbot feature localized
Verify that the Chatbot feature is properly localized
"""
import logging
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3341236"


def test_chatbot_feature_localized(about_prefs: AboutPrefs):
    """
    C3341236 - Chatbot feature localized
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.element_exists("ai-control-sidebar-chatbot-select")
    logging.info("Chatbot feature is localized")
