"""
C3341232 - Smart tab groups not displayed for non en builds
Verify that the Smart Tab groups suggestions feature is not displayed on the AI controls page for builds that don't start with en*
"""
import pytest
from selenium.common.exceptions import TimeoutException
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3341232"


@pytest.mark.skip(reason="Not run against non-en builds")
def test_smart_tab_groups_not_displayed_for_non_en_builds(about_prefs: AboutPrefs):
    """
    C3341232 - Smart tab groups not displayed for non en builds
    """
    about_prefs.navigate_to_ai_controls()

    try:
        about_prefs.get_element("ai-control-smart-tab-groups-select")
        raise AssertionError("Smart Tab Groups control should not be present in non-en builds")
    except TimeoutException:
        pass  # Expected: element not found in non-en builds
