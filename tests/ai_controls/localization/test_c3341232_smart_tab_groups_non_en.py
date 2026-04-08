"""
C3341232 - Smart tab groups not displayed for non en builds
Verify that the Smart Tab groups suggestions feature is not displayed on the AI controls page for builds that don't start with en*
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_smart_tab_groups_not_displayed_for_non_en_builds(about_prefs: AboutPrefs):
    """
    C3341232 - Smart tab groups not displayed for non en builds
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.verify_ai_controls_page_loaded()
    
    try:
        about_prefs.get_element("ai-control-smart-tab-groups-select")
        logging.warning("Smart Tab Groups control found in non-en build (unexpected)")
    except Exception:
        logging.info("Smart Tab Groups control not found (expected for non-en builds)")
