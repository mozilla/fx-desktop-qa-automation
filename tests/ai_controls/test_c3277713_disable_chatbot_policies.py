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


@pytest.fixture()
def policies_list():
    return {
        "AIControls": {
            "SidebarChatbot": {"Value": "blocked", "Locked": True}
        }
    }


def test_disable_only_chatbot_via_policies(about_prefs: AboutPrefs):
    """
    C3277713 - Disable only chatbot via policies
    Requires enterprise policy to disable only the chatbot feature.
    """
    about_prefs.navigate_to_ai_controls(verify=False)

    # Chatbot control should be hidden when the chatbot policy is active
    about_prefs.element_not_visible("ai-control-sidebar-chatbot-select")

    # Other features should remain available
    state = about_prefs.get_ai_translations_state()
    logging.info(f"Translations feature state (should still be available): {state}")
    assert state in ("available", "default"), (
        f"Translations should remain available when only chatbot is disabled by policy, got '{state}'"
    )
