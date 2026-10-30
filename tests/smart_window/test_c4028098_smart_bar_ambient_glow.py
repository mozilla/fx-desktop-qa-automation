"""
C4028098 - Smart Bar ambient glow
Verify the Smart Bar renders with its NOVA ambient glow, matching the reference
image for the current colour scheme.
"""

import platform

import pytest
from selenium.webdriver import Firefox

from auto_fxui.browser_object import SmartWindow
from auto_fxui.visual_baseline import VisualBaseline

pytestmark = pytest.mark.skipif(
    platform.system() != "Darwin",
    reason="Visual baselines have only been captured for macOS so far.",
)


@pytest.fixture()
def test_case():
    return "4028098"


@pytest.fixture()
def add_to_prefs_list():
    # The glow animates. Reduced motion settles it so a single frame is a
    # stable reference rather than whichever point of the animation we caught.
    return [("ui.prefersReducedMotion", 1)]


def test_smart_bar_ambient_glow(
    driver: Firefox, smart_window: SmartWindow, visual_baseline: VisualBaseline
):
    """
    C4028098 - Smart Bar ambient glow
    """
    smart_window.activate_smart_window()
    # The Smart Bar is only injected once the chat surface is opened; before
    # that ai-window-box has no size and cannot be captured at all.
    smart_window.click_on("smart-window-ask-button")
    smart_window.element_visible("smart-window-box")

    with driver.context(driver.CONTEXT_CHROME):
        box = smart_window.get_element("smart-window-box")
        visual_baseline.expect_matches(box, "smart-bar-glow")
