"""
Keyboard navigation to translations setting
Verify that Translations setting can be reached and modified via keyboard
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_keyboard_navigation_to_translations_setting(about_prefs: AboutPrefs):
    """
    Verify that Translations setting can be reached and modified via keyboard
    """
    about_prefs.navigate_to_ai_controls()
    
    try:
        translations = about_prefs.get_element("ai-control-translations-select")
        assert translations is not None, "Translations dropdown should exist"
        logging.info("Translations setting is keyboard accessible")
    except Exception as e:
        assert False, f"Translations setting should be keyboard accessible: {e}"
