"""
C3298825 - Disable only translations via policies
Verify that the user can disable only the Translations feature via policies
"""
import logging
import pytest
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3298825"


@pytest.fixture()
def policies_list():
    return {
        "AIControls": {
            "Translations": {"Value": "blocked", "Locked": True}
        }
    }


def test_disable_only_translations_via_policies(about_prefs: AboutPrefs):
    """
    C3298825 - Disable only translations via policies
    Requires enterprise policy to disable only the Translations feature.
    """
    about_prefs.navigate_to_ai_controls(verify=False)

    # Translations control should be hidden when the policy is active
    about_prefs.element_not_visible("ai-control-translations-select")
    logging.info("Translations control is not visible under policy")
