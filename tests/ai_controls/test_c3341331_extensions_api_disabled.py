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
    # TODO: Implement the following to complete this test:
    # 1. After blocking, read the extensions.ml.enabled pref via
    #    driver.execute_script("return Services.prefs.getBoolPref('extensions.ml.enabled');").
    # 2. Assert the pref is False when the killswitch is active.
    # 3. Unblock, then assert the pref returns to True.
