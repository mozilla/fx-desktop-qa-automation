"""
C3310314 - Enabled features remain after unblock
Verify that Enabled features remain Enabled after unblocking All AI features from the Kill Switch
"""
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3310314"


def test_enabled_features_remain_after_unblock(about_prefs: AboutPrefs):
    """
    C3310314 - Enabled features remain after unblock
    """
    about_prefs.navigate_to_ai_controls()

    about_prefs.set_ai_translations("enabled")
    translations_state_before = about_prefs.get_ai_translations_state()

    about_prefs.set_ai_blocking(True)
    about_prefs.expect(lambda _: about_prefs.get_ai_killswitch_state() is True)

    about_prefs.set_ai_blocking(False)
    about_prefs.expect(lambda _: about_prefs.get_ai_killswitch_state() is False)

    translations_state_after = about_prefs.get_ai_translations_state()
    assert translations_state_after == translations_state_before, (
        f"Translations state changed after unblock: "
        f"was '{translations_state_before}', now '{translations_state_after}'"
    )
