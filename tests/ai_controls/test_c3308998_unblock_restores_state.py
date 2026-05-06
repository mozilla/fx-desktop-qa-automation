import pytest


@pytest.fixture()
def test_case():
    return "C3308998"


def test_unblock_restores_state(about_prefs):
    """Verify that unblocking AI restores the toggle to unpressed state."""
    about_prefs.navigate_to_ai_controls()

    # Block AI features
    about_prefs.set_ai_blocking(block=True)
    assert about_prefs.get_ai_killswitch_state() is True

    # Unblock AI features
    about_prefs.set_ai_blocking(block=False)
    assert about_prefs.get_ai_killswitch_state() is False
