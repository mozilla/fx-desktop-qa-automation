"""
C3276004 - AI settings link shortcut visible
Verify that the AI settings link/shortcut is visible on the Firefox Preferences page
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_ai_settings_link_shortcut_visible(about_prefs: AboutPrefs):
    """
    C3276004 - AI settings link shortcut visible
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.verify_ai_controls_page_loaded()
    logging.info("AI settings link/shortcut is visible on preferences page")
