"""
C3341235 - Translations feature localized
Verify that the Translations feature is properly localized
"""
import logging
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3341235"


def test_translations_feature_localized(about_prefs: AboutPrefs):
    """
    C3341235 - Translations feature localized
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.element_exists("ai-control-translations-select")
    logging.info("Translations feature is localized")
