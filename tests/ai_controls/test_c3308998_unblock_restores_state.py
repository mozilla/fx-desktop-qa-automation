import pytest


@pytest.fixture()
def test_case():
    return "3308998"


def test_unblock_restores_state(about_prefs):
    """Verify that clicking the AI killswitch toggle blocks/unblocks AI
    features and that the downstream select controls become disabled/enabled
    accordingly."""
    # Initial state: AI should be available (toggle unpressed, selects enabled)
    about_prefs.expect_ai_killswitch_state(pressed=False)
    about_prefs.expect_ai_selects_state(disabled=False)

    # Block AI
    about_prefs.toggle_ai_killswitch_click()
    about_prefs.expect_ai_killswitch_state(pressed=True)
    about_prefs.expect_ai_selects_state(disabled=True)

    # Unblock AI
    about_prefs.toggle_ai_killswitch_click()
    about_prefs.expect_ai_killswitch_state(pressed=False)
    about_prefs.expect_ai_selects_state(disabled=False)
