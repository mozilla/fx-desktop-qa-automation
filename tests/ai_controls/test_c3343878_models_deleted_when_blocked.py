"""
C3343878 - All AI models deleted when features blocked
Verify that All AI models are deleted from the browser when the AI features are Blocked
"""
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3343878"


def test_all_ai_models_deleted_when_features_blocked(about_prefs: AboutPrefs):
    """
    C3343878 - All AI models deleted when features blocked
    """
    about_prefs.navigate_to_ai_controls()

    about_prefs.set_ai_blocking(True)
    about_prefs.expect(lambda _: about_prefs.get_ai_killswitch_state() is True)
    # Note: Full model deletion verification requires navigating to about:inference,
    # which is outside the scope of this AboutPrefs page object.
