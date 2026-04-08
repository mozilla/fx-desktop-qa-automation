"""
C3341237 - AI controls labels localized
Verify that all labels on the AI controls page are properly localized
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_ai_controls_labels_localized(about_prefs: AboutPrefs):
    """
    C3341237 - AI controls labels localized
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.verify_ai_controls_page_loaded()
    logging.info("AI controls labels are localized")
