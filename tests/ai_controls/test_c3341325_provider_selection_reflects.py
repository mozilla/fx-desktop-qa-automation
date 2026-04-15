"""
C3341325 - Chatbot provider selection reflects on AI controls page
Verify that selecting an AI model in the Sidebar will reflect the users choice on the AI controls page
"""
import logging
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3341325"


def test_chatbot_provider_selection_reflects_on_ai_controls_page(about_prefs: AboutPrefs):
    """
    C3341325 - Chatbot provider selection reflects on AI controls page
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.verify_ai_controls_page_loaded()

    about_prefs.element_exists("ai-control-sidebar-chatbot-select")
    about_prefs.set_ai_chatbot_provider("ChatGPT")
    logging.info("Chatbot provider set via AI controls page")
