"""
C3262007 - Block all GenAI features at the same time
Verify that blocking all AI features from AI Controls blocks every feature
listed on the page.
"""

import pytest
from auto_fxui.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "3262007"


def test_block_all_genai_features(about_prefs: AboutPrefs):
    """
    C3262007 - Block all GenAI features at the same time
    """
    about_prefs.navigate_to_ai_controls()

    about_prefs.element_visible("ai-controls-description")
    about_prefs.element_visible("ai-controls-learn-more-link")
    about_prefs.expect_ai_killswitch_state(pressed=False)
    about_prefs.element_not_visible("ai-controls-blocked-message")

    features_before = about_prefs.get_ai_feature_states()
    assert features_before, "no AI features are listed on the page"

    about_prefs.toggle_ai_killswitch_click()
    about_prefs.expect_ai_killswitch_state(pressed=True)
    about_prefs.element_visible("ai-controls-blocked-message")

    about_prefs.expect(
        lambda _: set(about_prefs.get_ai_feature_states().values()) == {"blocked"}
    )
    assert set(about_prefs.get_ai_feature_states()) == set(features_before)
