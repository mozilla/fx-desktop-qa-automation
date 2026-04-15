"""
C3277714 - Disable only smart tab groups via policies
Verify that the user can disable only the Smart Tab groups feature via policies
"""
import logging
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3277714"


def test_disable_only_smart_tab_groups_via_policies(about_prefs: AboutPrefs):
    """
    C3277714 - Disable only smart tab groups via policies
    Stub: requires enterprise policy to disable only the Smart Tab Groups feature.
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.verify_ai_controls_page_loaded()
    logging.info("Stub: full validation requires enterprise policy configuration")
