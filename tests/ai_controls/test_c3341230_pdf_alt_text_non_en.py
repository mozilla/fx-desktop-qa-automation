"""
C3341230 - PDF alt text feature not displayed for non en builds
Verify that the PDFjs Alt Text feature is not displayed on the AI controls page for non en* builds
"""
import pytest
from selenium.common.exceptions import TimeoutException
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3341230"


@pytest.mark.skip(reason="Not run against non-en builds")
def test_pdf_alt_text_feature_not_displayed_for_non_en_builds(about_prefs: AboutPrefs):
    """
    C3341230 - PDF alt text feature not displayed for non en builds
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.verify_ai_controls_page_loaded()

    try:
        about_prefs.get_element("ai-control-pdf-alt-text-select")
        raise AssertionError("PDF alt text control should not be present in non-en builds")
    except TimeoutException:
        pass  # Expected: element not found in non-en builds
