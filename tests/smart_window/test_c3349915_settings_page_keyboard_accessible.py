"""
C3349915 - Settings page keyboard accessible
Verify the Smart Window controls in AI settings can be reached by TAB and
respond to focus.
"""

import logging

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.page_object import AboutPrefs

MAX_TAB_STOPS = 30


@pytest.fixture()
def test_case():
    return "3349915"


def _focused_matches(driver, element) -> bool:
    """True when `element`, or a host of the focused control, has focus."""
    active = driver.switch_to.active_element
    if active == element:
        return True
    # moz-select and friends keep the real control in a shadow root, so
    # activeElement reports the host rather than the control.
    return bool(
        driver.execute_script(
            """
            const active = arguments[0];
            let node = arguments[1];
            while (node) {
                if (node === active) return true;
                const root = node.getRootNode && node.getRootNode();
                node = root && root.host ? root.host : node.parentNode;
            }
            return false;
            """,
            active,
            element,
        )
    )


def test_settings_page_keyboard_accessible(driver: Firefox):
    """
    C3349915 - Settings page keyboard accessible
    """
    about_prefs = AboutPrefs(driver, category="ai").open()
    about_prefs.navigate_to_ai_controls()

    select = about_prefs.get_element("ai-control-smart-window-select")
    targets = {
        "Activate Smart Window link": about_prefs.get_element(
            "smart-window-activate-link"
        ),
    }

    about_prefs.driver.execute_script("arguments[0].focus();", select)
    about_prefs.expect(lambda d: _focused_matches(d, select))
    logging.info("Smart Window select is keyboard-focusable")

    # Only assert that TAB reaches each control, not that they are adjacent:
    # the rows between them are feature-gated and some are hidden while
    # signed out.
    for _ in range(MAX_TAB_STOPS):
        if not targets:
            break
        about_prefs.actions.send_keys(Keys.TAB).perform()
        reached = [
            name
            for name, element in targets.items()
            if _focused_matches(about_prefs.driver, element)
        ]
        for name in reached:
            logging.info("%s is keyboard-focusable", name)
            del targets[name]

    assert not targets, (
        f"not reachable by TAB within {MAX_TAB_STOPS} stops: {sorted(targets)}"
    )
