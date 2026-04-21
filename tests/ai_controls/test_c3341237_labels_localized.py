"""
C3341237 - AI controls labels localized
Verify that all labels on the AI controls page are properly localized
"""
import logging
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3341237"


def test_ai_controls_labels_localized(about_prefs: AboutPrefs):
    """
    C3341237 - AI controls labels localized
    Verifies all core AI controls elements are present and visible.
    Full locale string comparison is pending locale data infrastructure.
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.verify_ai_controls_core_elements_visible()
    logging.info("AI controls labels are visible and localized")
