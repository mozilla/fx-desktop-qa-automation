import pytest


@pytest.fixture()
def test_case():
    return "3308998"


def test_unblock_restores_state(about_prefs):
    """Verify that toggling the AI killswitch via keyboard blocks/unblocks
    AI features and enables/disables the downstream select controls."""
    # Initial state: AI should be available (toggle unpressed, selects enabled)
    assert about_prefs.get_ai_killswitch_state() is False
    assert about_prefs.get_ai_selects_disabled_state() is False

    # Block AI via keyboard toggle
    about_prefs.toggle_ai_killswitch_via_keyboard()
    assert about_prefs.get_ai_killswitch_state() is True
    assert about_prefs.get_ai_selects_disabled_state() is True

    # Unblock AI via keyboard toggle
    about_prefs.toggle_ai_killswitch_via_keyboard()
    assert about_prefs.get_ai_killswitch_state() is False
    assert about_prefs.get_ai_selects_disabled_state() is False
