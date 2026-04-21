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


@pytest.fixture()
def policies_list():
    return {
        "AIControls": {
            "Default": {"Value": "blocked", "Locked": True}
        }
    }


def test_disable_all_ai_features_via_policies(about_prefs: AboutPrefs):
    """
    C3277712 - Disable all AI features via policies
    With AIControls.Default blocked, all individual feature controls should
    be hidden from the AI controls page.
    """
    about_prefs.navigate_to_ai_controls(verify=False)

    about_prefs.element_not_visible("ai-control-translations-select")
    about_prefs.element_not_visible("ai-control-sidebar-chatbot-select")
    about_prefs.element_not_visible("ai-control-link-preview-select")
    about_prefs.element_not_visible("ai-control-smart-tab-groups-select")
    logging.info("All AI feature controls are hidden under AIControls Default blocked policy")
