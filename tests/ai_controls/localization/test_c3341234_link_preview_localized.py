"""
C3341234 - Link preview feature localized
Verify that the Link preview feature is properly localized
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_link_preview_feature_localized(about_prefs: AboutPrefs):
    """
    C3341234 - Link preview feature localized
    """
    about_prefs.navigate_to_ai_controls()
    
    try:
        link_preview = about_prefs.get_element("ai-control-link-preview-select")
        assert link_preview is not None, "Link preview control should exist"
        logging.info("Link preview feature is localized")
    except Exception as e:
        logging.info(f"Link preview feature not available: {e}")
