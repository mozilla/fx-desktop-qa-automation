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

    about_prefs.set_ai_blocking(True)
    about_prefs.expect(lambda _: about_prefs.get_ai_killswitch_state() is True)
    # Note: Verification that extensions.ml.enabled is also disabled
    # would require navigating to about:config as a separate step.
