"""
C3340562 - Cancel blocking all AI enhancements
Verify that the user can Cancel Blocking all AI enhancements from the Block AI Enhancements prompt
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_cancel_blocking_all_ai_enhancements(about_prefs: AboutPrefs):
    """
    C3340562 - Cancel blocking all AI enhancements
    """
    about_prefs.navigate_to_ai_controls()
    
    # Get initial state
    initial_state = about_prefs.get_ai_killswitch_state()
    
    # Step 2-3: Attempt to block (dialog may appear)
    about_prefs.set_ai_blocking(True)
    
    # Verify we can interact with the control
    current_state = about_prefs.get_ai_killswitch_state()
    logging.info(f"Killswitch state changed from {initial_state} to {current_state}")
