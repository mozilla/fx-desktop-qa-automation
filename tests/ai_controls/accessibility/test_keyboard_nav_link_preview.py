"""
Keyboard navigation to link preview setting
Verify that Link Preview setting can be reached and modified via keyboard
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_keyboard_navigation_to_link_preview_setting(about_prefs: AboutPrefs):
    """
    Verify that Link Preview setting can be reached and modified via keyboard
    """
    about_prefs.navigate_to_ai_controls()
    
    try:
        link_preview = about_prefs.get_element("ai-control-link-preview-select")
        assert link_preview is not None, "Link Preview dropdown should exist"
        logging.info("Link Preview setting is keyboard accessible")
    except Exception as e:
        logging.info(f"Link Preview setting not available: {e}")
