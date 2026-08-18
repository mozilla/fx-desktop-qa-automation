"""
C3341331 - Web extensions AI API disabled when blocking
Verify that the Web Extensions AI API is disabled when Blocking all AI enhancements
"""

import pytest

from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3341331"


def test_web_extensions_ai_api_disabled_when_blocking(about_prefs: AboutPrefs):
    """
    C3341331 - Web extensions AI API disabled when blocking
    """
    about_prefs.navigate_to_ai_controls()

    # Precondition: the WebExtensions ML API is enabled before we block, so the
    # transition below is meaningful (fails loudly here if the default changes).
    about_prefs.expect(lambda _: about_prefs.get_extensions_ml_enabled() == True)

    # Block via the UI toggle (not a raw pref) so the killswitch side effects
    # run, then confirm the WebExtensions ML API is disabled.
    about_prefs.toggle_ai_killswitch_click()
    about_prefs.expect_ai_killswitch_state(pressed=True)
    about_prefs.expect(lambda _: about_prefs.get_extensions_ml_enabled() == False)

    # Unblocking restores the API.
    about_prefs.toggle_ai_killswitch_click()
    about_prefs.expect_ai_killswitch_state(pressed=False)
    about_prefs.expect(lambda _: about_prefs.get_extensions_ml_enabled() == True)
