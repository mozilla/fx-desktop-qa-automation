"""
C3277716 - Disable only link previews via policies
Verify that the user can disable only the Link previews feature via policies
"""
import logging
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3277716"


@pytest.fixture()
def policies_list():
    return {
        "AIControls": {
            "LinkPreviewKeyPoints": {"Value": "blocked", "Locked": True}
        }
    }


def test_disable_only_link_previews_via_policies(about_prefs: AboutPrefs):
    """
    C3277716 - Disable only link previews via policies
    Requires enterprise policy to disable only the Link Previews feature.
    """
    about_prefs.navigate_to_ai_controls(verify=False)

    # Link Preview control should be hidden when the policy is active
    about_prefs.element_not_visible("ai-control-link-preview-select")
    logging.info("Link Preview control is not visible under policy")
