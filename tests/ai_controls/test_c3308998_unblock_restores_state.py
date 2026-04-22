"""
C3308998 - Unblock all AI features restores state
Verify that AI features show the Available status after unblocking all AI features
"""
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3308998"


def test_unblock_all_ai_features_restores_state(about_prefs: AboutPrefs):
    """
    C3308998 - Unblock all AI features restores state
    """
    about_prefs.navigate_to_ai_controls()

    about_prefs.set_ai_blocking(False)
    about_prefs.set_ai_blocking(True)
    about_prefs.expect(lambda _: about_prefs.get_ai_killswitch_state() is True)

    about_prefs.set_ai_blocking(False)
    about_prefs.expect(lambda _: about_prefs.get_ai_killswitch_state() is False)
