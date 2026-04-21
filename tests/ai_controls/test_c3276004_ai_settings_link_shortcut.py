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
    # TODO: Implement the following to complete this test:
    # 1. Navigate to about:preferences (without #ai hash).
    # 2. Assert that the AI controls category link (category-ai-features) is
    #    visible in the left sidebar.
    # 3. Click the link and assert it navigates to the #ai pane.
    about_prefs.navigate_to_ai_controls()
    about_prefs.verify_ai_controls_core_elements_visible()
    logging.info("AI settings page loaded — sidebar shortcut assertion pending")
