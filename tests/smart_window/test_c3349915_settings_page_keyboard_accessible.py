"""
C3349915 - Settings page keyboard accessible
Verify the Smart Window controls in AI settings can be reached by TAB.
"""

import logging

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.page_object import AboutPrefs

# Measured: the select is stop 16 and the link 17. 40 leaves room for rows
# that appear when other AI features are enabled.
MAX_TAB_STOPS = 40


@pytest.fixture()
def test_case():
    return "3349915"


def test_settings_page_keyboard_accessible(driver: Firefox):
    """
    C3349915 - Settings page keyboard accessible
    """
    about_prefs = AboutPrefs(driver, category="ai").open()
    about_prefs.navigate_to_ai_controls()

    targets = {
        "Smart Window select": about_prefs.get_element(
            "ai-control-smart-window-select"
        ),
        "Activate Smart Window link": about_prefs.get_element(
            "smart-window-activate-link"
        ),
    }

    # TAB from where the page starts, rather than seeding focus, so this
    # follows the route a keyboard user actually takes.
    for _ in range(MAX_TAB_STOPS):
        if not targets:
            break
        about_prefs.actions.send_keys(Keys.TAB).perform()
        for name in [
            n for n, el in targets.items() if about_prefs.utils.element_has_focus(el)
        ]:
            logging.info("%s is keyboard-focusable", name)
            del targets[name]

    assert not targets, (
        f"not reachable by TAB within {MAX_TAB_STOPS} stops: {sorted(targets)}"
    )
