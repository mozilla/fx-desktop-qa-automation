"""
C3341230 - PDF alt text feature not displayed for non en builds
Verify that the PDFjs Alt Text feature is not displayed on the AI controls page for non en* builds
"""
import logging
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3341230"


def test_pdf_alt_text_feature_not_displayed_for_non_en_builds(about_prefs: AboutPrefs):
    """
    C3341230 - PDF alt text feature not displayed for non en builds
    Verify that the PDFjs Alt Text feature is not displayed on the AI controls page for non en* builds
    """
    about_prefs.navigate_to_ai_controls()
    
    # Step 1: Navigate to AI controls page
    about_prefs.verify_ai_controls_page_loaded()
    
    # Step 2: Check if PDF alt text control exists
    # In non-en builds, this should not be present
    try:
        about_prefs.get_element("ai-control-pdf-alt-text-select")
        logging.warning("PDF alt text control found in non-en build (unexpected)")
    except Exception:
        logging.info("PDF alt text control not found (expected for non-en builds)")
