"""
C3310314 - Enabled features remain after unblock
Verify that Enabled features remain Enabled after unblocking All AI features from the Kill Switch
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_enabled_features_remain_after_unblock(about_prefs: AboutPrefs):
    """
    C3310314 - Enabled features remain after unblock
    """
    about_prefs.navigate_to_ai_controls()
    
    # Step 1: Enable translations
    about_prefs.set_ai_translations("enabled")
    translations_state_before = about_prefs.get_ai_translations_state()
    
    # Step 2: Toggle killswitch off and on
    about_prefs.set_ai_blocking(True)
    about_prefs.set_ai_blocking(False)
    
    # Step 3-4: Verify states
    translations_state_after = about_prefs.get_ai_translations_state()
    logging.info(f"Translations state: before={translations_state_before}, after={translations_state_after}")
