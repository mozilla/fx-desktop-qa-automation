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


def test_disable_only_link_previews_via_policies(about_prefs: AboutPrefs):
    """
    C3277716 - Disable only link previews via policies
    Stub: requires enterprise policy to disable only the Link Previews feature.
    """
    about_prefs.navigate_to_ai_controls()
    about_prefs.verify_ai_controls_page_loaded()
    logging.info("Stub: full validation requires enterprise policy configuration")
