"""
C3279955 - Enable AI features when policy changed
Verify that the AI features can be enabled if the policy is changed or removed
"""
import logging
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3279955"


@pytest.fixture()
def policies_list():
    """No policy active — simulates policy being removed/changed."""
    return {}


def test_enable_ai_features_when_policy_changed(about_prefs: AboutPrefs):
    """
    C3279955 - Enable AI features when policy changed
    """
    about_prefs.navigate_to_ai_controls()

    # With no restricting policy active, the killswitch should be off
    killswitch_state = about_prefs.get_ai_killswitch_state()
    assert killswitch_state is False, (
        "Killswitch should be off when no restricting policy is active"
    )
    logging.info(f"Killswitch state after policy change: {killswitch_state}")
