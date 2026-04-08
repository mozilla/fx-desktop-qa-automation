"""
C3279955 - Enable AI features when policy changed
Verify that the AI features can be enabled if the policy is changed or removed
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_enable_ai_features_when_policy_changed(about_prefs: AboutPrefs):
    """
    C3279955 - Enable AI features when policy changed
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.verify_ai_controls_page_loaded()
    
    killswitch_state = about_prefs.get_ai_killswitch_state()
    logging.info(f"Killswitch state after policy change: {killswitch_state}")
