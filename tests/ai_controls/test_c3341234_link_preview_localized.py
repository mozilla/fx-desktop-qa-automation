"""
C3341234 - Link preview feature localized
Verify that the Link preview feature is properly localized
"""
import logging
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3341234"


def test_link_preview_feature_localized(about_prefs: AboutPrefs):
    """
    C3341234 - Link preview feature localized
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.element_exists("ai-control-link-preview-select")
    logging.info("Link preview feature is localized")
