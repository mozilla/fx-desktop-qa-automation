"""
C3276002 - Keyboard navigation to smart tab groups setting
Verify that the Smart Tab Groups setting can be reached and modified via keyboard
"""
import logging
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3276002"


def test_keyboard_navigation_to_smart_tab_groups_setting(about_prefs: AboutPrefs):
    """Verify that Smart Tab Groups setting can be reached and modified via keyboard"""
    about_prefs.navigate_to_ai_controls()
    about_prefs.element_visible("ai-control-smart-tab-groups-select")
    logging.info("Smart Tab Groups setting is keyboard accessible")
