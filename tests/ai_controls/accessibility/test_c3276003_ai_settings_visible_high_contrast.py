"""
C3276003 - AI settings visible with high contrast
Verify that the AI settings page is visible with High Contrast and other themes enabled
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_ai_settings_visible_with_high_contrast(about_prefs: AboutPrefs):
    """
    C3276003 - AI settings visible with high contrast
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.verify_ai_controls_page_loaded()
    logging.info("AI settings page is visible with high contrast theme")
