"""
C3277713 - Disable only chatbot via policies
Verify that the user can disable only the Chatbot feature via policies
"""
import logging
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3277713"


def test_disable_only_chatbot_via_policies(about_prefs: AboutPrefs):
    """
    C3277713 - Disable only chatbot via policies
    Stub: requires enterprise policy to disable only the chatbot feature.
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.verify_ai_controls_page_loaded()

    # When only chatbot is disabled by policy, translations should still be available
    state = about_prefs.get_ai_translations_state()
    logging.info(f"Translations feature state: {state}")
    # Note: Full validation requires enterprise policy configuration in the browser profile.
