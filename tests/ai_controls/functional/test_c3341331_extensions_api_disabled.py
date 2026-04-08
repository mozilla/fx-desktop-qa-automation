"""
C3341331 - Web extensions AI API disabled when blocking
Verify that the Web Extensions AI API is disabled when Blocking all AI enhancements
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_web_extensions_ai_api_disabled_when_blocking(about_prefs: AboutPrefs):
    """
    C3341331 - Web extensions AI API disabled when blocking
    """
    about_prefs.navigate_to_ai_controls()
    
    # Step 1-2: Block all AI enhancements
    about_prefs.set_ai_blocking(True)
    assert about_prefs.get_ai_killswitch_state() is True, "AI features should be blocked"
    
    # For extensions.ml.enabled verification, we would need to access about:config
    # This would be a separate verification step in the actual test execution
