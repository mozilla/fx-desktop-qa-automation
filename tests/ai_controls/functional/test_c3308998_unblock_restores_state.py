"""
C3308998 - Unblock all AI features restores state
Verify that AI features show the Available status after unblocking all AI features
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_unblock_all_ai_features_restores_state(about_prefs: AboutPrefs):
    """
    C3308998 - Unblock all AI features restores state
    """
    about_prefs.navigate_to_ai_controls()
    
    # Step 1-2: Enable features then block all
    about_prefs.set_ai_blocking(False)
    about_prefs.set_ai_blocking(True)
    assert about_prefs.get_ai_killswitch_state() is True, "All AI features should be blocked"
    
    # Step 4-5: Unblock features
    about_prefs.set_ai_blocking(False)
    assert about_prefs.get_ai_killswitch_state() is False, "AI features should be available"
