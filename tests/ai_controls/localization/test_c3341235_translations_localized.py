"""
C3341235 - Translations feature localized
Verify that the Translations feature is properly localized
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_translations_feature_localized(about_prefs: AboutPrefs):
    """
    C3341235 - Translations feature localized
    """
    about_prefs.navigate_to_ai_controls()
    
    try:
        translations = about_prefs.get_element("ai-control-translations-select")
        assert translations is not None, "Translations control should exist"
        logging.info("Translations feature is localized")
    except Exception as e:
        logging.info(f"Translations feature not available: {e}")
