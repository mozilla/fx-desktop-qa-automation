"""
C3298824 - Block all AI features option persists
Verify that the Block all AI features option remains enabled after enabling one of the features
"""

import pytest

from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3298824"


def test_block_all_ai_features_option_persists(about_prefs: AboutPrefs):
    """
    C3298824 - Block all AI features option persists
    """
    about_prefs.navigate_to_ai_controls()

    # Block via the UI toggle so the killswitch's real side effects fire
    # (matches the pattern used in C3310314 / C3341331).
    about_prefs.toggle_ai_killswitch_click()
    about_prefs.expect_ai_killswitch_state(pressed=True)

    # Enable one individual feature via pref — its UI control is hidden while
    # the killswitch is active, so set (and read back) the pref directly.
    about_prefs.driver.execute_script(
        "Services.prefs.setStringPref('browser.ai.control.translations', 'available');"
    )
    about_prefs.expect(
        lambda _: about_prefs.driver.execute_script(
            "return Services.prefs.getStringPref('browser.ai.control.translations', '');"
        )
        == "available"
    )

    # Enabling an individual feature must NOT clear the global Block-all toggle.
    about_prefs.expect_ai_killswitch_state(pressed=True)
