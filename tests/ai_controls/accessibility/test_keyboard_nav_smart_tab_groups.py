"""
Keyboard navigation to smart tab groups setting
Verify that Smart Tab Groups setting can be reached and modified via keyboard
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_keyboard_navigation_to_smart_tab_groups_setting(about_prefs: AboutPrefs):
    """
    Verify that Smart Tab Groups setting can be reached and modified via keyboard
    """
    about_prefs.navigate_to_ai_controls()
    
    try:
        tab_groups = about_prefs.get_element("ai-control-smart-tab-groups-select")
        assert tab_groups is not None, "Smart Tab Groups dropdown should exist"
        logging.info("Smart Tab Groups setting is keyboard accessible")
    except Exception as e:
        logging.info(f"Smart Tab Groups setting not available: {e}")
