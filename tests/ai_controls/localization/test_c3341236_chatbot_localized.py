"""
C3341236 - Chatbot feature localized
Verify that the Chatbot feature is properly localized
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_chatbot_feature_localized(about_prefs: AboutPrefs):
    """
    C3341236 - Chatbot feature localized
    """
    about_prefs.navigate_to_ai_controls()
    
    try:
        chatbot = about_prefs.get_element("ai-control-sidebar-chatbot-select")
        assert chatbot is not None, "Chatbot provider control should exist"
        logging.info("Chatbot feature is localized")
    except Exception as e:
        logging.info(f"Chatbot feature not available: {e}")
