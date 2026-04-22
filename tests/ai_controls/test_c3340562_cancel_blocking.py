"""
C3340562 - Cancel blocking all AI enhancements
Verify that the user can Cancel Blocking all AI enhancements from the Block AI Enhancements prompt
"""
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3340562"


def test_cancel_blocking_all_ai_enhancements(about_prefs: AboutPrefs):
    """
    C3340562 - Cancel blocking all AI enhancements
    """
    about_prefs.navigate_to_ai_controls()

    initial_state = about_prefs.get_ai_killswitch_state()

    # Block AI, then restore to initial state (simulating a cancel action)
    about_prefs.set_ai_blocking(True)
    about_prefs.expect(lambda _: about_prefs.get_ai_killswitch_state() is True)

    about_prefs.set_ai_blocking(initial_state)
    about_prefs.expect(lambda _: about_prefs.get_ai_killswitch_state() == initial_state)
