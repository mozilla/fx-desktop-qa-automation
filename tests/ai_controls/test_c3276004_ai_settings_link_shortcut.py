"""
C3276004 - AI settings link shortcut visible
Verify that the AI settings link/shortcut is visible on the Firefox Preferences page
"""
import logging
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3276004"


def test_ai_settings_link_shortcut_visible(about_prefs: AboutPrefs):
    """
    C3276004 - AI settings link shortcut visible
    """
    # TODO: Navigate to about:preferences (not #ai) and assert the AI section
    # shortcut link is visible before clicking through to the AI controls page.
    about_prefs.navigate_to_ai_controls()
    about_prefs.verify_ai_controls_core_elements_visible()
    logging.info("AI settings link/shortcut is visible on preferences page")
