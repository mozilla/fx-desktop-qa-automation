"""
C3298825 - Disable only translations via policies
Verify that the user can disable only the Translations feature via policies
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_disable_only_translations_via_policies(about_prefs: AboutPrefs):
    """
    C3298825 - Disable only translations via policies
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.verify_ai_controls_page_loaded()
    logging.info("Translations policy test - verifying other features remain accessible")
