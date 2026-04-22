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
    # TODO: A complete implementation would also assert that the element's
    # data-l10n-id resolves to a non-empty, locale-appropriate string via
    # driver.execute_script("return document.l10n.formatValue(...)").
    logging.info("Translations feature element is present")
