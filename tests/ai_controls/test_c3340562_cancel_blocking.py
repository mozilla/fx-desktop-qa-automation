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

    # AI starts unblocked. Click the killswitch and Cancel the confirmation
    # prompt; the toggle must not flip and the feature selects stay enabled.
    about_prefs.expect_ai_killswitch_state(pressed=False)
    about_prefs.cancel_ai_killswitch_click()
    about_prefs.expect_ai_killswitch_state(pressed=False)
    about_prefs.expect_ai_selects_state(disabled=False)
