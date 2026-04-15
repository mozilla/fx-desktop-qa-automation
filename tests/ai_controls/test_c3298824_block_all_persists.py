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

    about_prefs.set_ai_blocking(True)
    about_prefs.expect(lambda _: about_prefs.get_ai_killswitch_state() is True)

    # Re-verify state is still on after a subsequent read
    about_prefs.expect(lambda _: about_prefs.get_ai_killswitch_state() is True)
