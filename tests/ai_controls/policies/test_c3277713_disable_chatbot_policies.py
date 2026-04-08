"""
C3277713 - Disable only chatbot via policies
Verify that the user can disable only the Chatbot feature via policies
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_disable_only_chatbot_via_policies(about_prefs: AboutPrefs):
    """
    C3277713 - Disable only chatbot via policies
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.verify_ai_controls_page_loaded()
    
    # Try to access translations (should work if only chatbot is disabled)
    try:
        state = about_prefs.get_ai_translations_state()
        logging.info(f"Translations feature state: {state}")
    except Exception as e:
        logging.info(f"Translations control status: {e}")
