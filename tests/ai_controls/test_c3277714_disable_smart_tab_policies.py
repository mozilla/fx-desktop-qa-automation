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


@pytest.fixture()
def policies_list():
    return {
        "AIControls": {
            "SmartTabGroups": {"Value": "blocked", "Locked": True}
        }
    }


def test_disable_only_smart_tab_groups_via_policies(about_prefs: AboutPrefs):
    """
    C3277714 - Disable only smart tab groups via policies
    Requires enterprise policy to disable only the Smart Tab Groups feature.
    """
    about_prefs.navigate_to_ai_controls()

    # Smart Tab Groups control should be hidden when the policy is active
    about_prefs.element_not_visible("ai-control-smart-tab-groups-select")
    logging.info("Smart Tab Groups control is not visible under policy")
