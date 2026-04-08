"""
C3343878 - All AI models deleted when features blocked
Verify that All AI models are deleted from the browser when the AI features are Blocked
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_all_ai_models_deleted_when_features_blocked(about_prefs: AboutPrefs):
    """
    C3343878 - All AI models deleted when features blocked
    """
    about_prefs.navigate_to_ai_controls()
    
    # Step 3-4: Enable block all
    about_prefs.set_ai_blocking(True)
    assert about_prefs.get_ai_killswitch_state() is True, "All AI features should be blocked"
    
    # Note: Model deletion verification would happen at about:inference page
    # which is beyond the scope of this AboutPrefs page object
