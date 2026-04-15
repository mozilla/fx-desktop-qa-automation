"""
C3277712 - Disable all AI features via policies
Verify that the user can Disable all AI feature settings via policies
"""
import logging
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3277712"


def test_disable_all_ai_features_via_policies(about_prefs: AboutPrefs):
    """
    C3277712 - Disable all AI features via policies
    Stub: requires enterprise policy (DisableAIEnhancements) to be set in profile.
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.verify_ai_controls_page_loaded()

    toggle_state = about_prefs.get_ai_killswitch_state()
    logging.info(f"Killswitch state under policy: {toggle_state}")
    # Note: When DisableAIEnhancements policy is active, killswitch should be forced on.
    # Full validation requires enterprise policy configuration in the browser profile.
