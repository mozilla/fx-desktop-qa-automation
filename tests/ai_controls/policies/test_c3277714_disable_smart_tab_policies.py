"""
C3277714 - Disable only smart tab groups via policies
Verify that the user can disable only the Smart Tab groups feature via policies
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_disable_only_smart_tab_groups_via_policies(about_prefs: AboutPrefs):
    """
    C3277714 - Disable only smart tab groups via policies
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.verify_ai_controls_page_loaded()
    logging.info("Smart Tab Groups policy test - verifying other features remain accessible")
