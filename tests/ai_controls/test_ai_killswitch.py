import pytest

from modules.page_object_prefs import AboutPrefs


def test_block_ai_enhancements_toggle(driver):
    """Simple smoke test for the AI Controls killswitch toggle.

    This test opens the AI Controls pane and toggles the global "Block AI enhancements"
    control on then off. It asserts the toggle's checked attribute reflects the action.
    """
    driver.get("about:preferences#paneAi")
    prefs = AboutPrefs(driver)

    # Ensure we can set block on
    prefs.set_ai_blocking(True)
    toggle = prefs.get_element("ai-controls-toggle")
    assert toggle.get_attribute("checked") in ("true", "checked", ""), "Expected AI block to be enabled"

    # Now disable blocking
    prefs.set_ai_blocking(False)
    toggle = prefs.get_element("ai-controls-toggle")
    assert toggle.get_attribute("checked") not in ("true", "checked", ""), "Expected AI block to be disabled"
