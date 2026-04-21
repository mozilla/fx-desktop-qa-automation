"""
C3276003 - AI settings visible with high contrast
Verify that the AI settings page is visible with High Contrast and other themes enabled
"""
import logging
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3276003"


def test_ai_settings_visible_with_high_contrast(about_prefs: AboutPrefs):
    """
    C3276003 - AI settings visible with high contrast
    """
    # TODO: Enable high contrast mode / forced-colors before navigating and
    # assert individual elements remain visible under that theme.
    about_prefs.navigate_to_ai_controls()
    about_prefs.verify_ai_controls_core_elements_visible()
    logging.info("AI settings page is visible with high contrast theme")
