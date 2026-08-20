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

    # Enable an individual feature.
    about_prefs.set_ai_translations("available")

    # Block, then unblock, all AI via the kill switch UI (not a direct pref
    # write) so the toggle's real side effects are exercised.
    about_prefs.toggle_ai_killswitch_click()
    about_prefs.expect_ai_killswitch_state(pressed=True)
    about_prefs.toggle_ai_killswitch_click()
    about_prefs.expect_ai_killswitch_state(pressed=False)

    # The previously-enabled feature must remain enabled after unblocking.
    about_prefs.expect(lambda _: about_prefs.get_ai_translations_state() == "available")
