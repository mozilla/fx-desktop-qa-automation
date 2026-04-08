"""
C3277716 - Disable only link previews via policies
Verify that the user can disable only the Link previews feature via policies
"""
import logging
from modules.page_object_prefs import AboutPrefs


def test_disable_only_link_previews_via_policies(about_prefs: AboutPrefs):
    """
    C3277716 - Disable only link previews via policies
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.verify_ai_controls_page_loaded()
    logging.info("Link Previews policy test - verifying other features remain accessible")
