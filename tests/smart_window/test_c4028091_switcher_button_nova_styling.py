"""
C4028091 - The Smart Window Switcher is updated to the new NOVA styling
Verify the Window Switcher button matches its NOVA reference image, and that
it visibly changes state when hovered and when pressed.
"""

import platform

import pytest
from selenium.webdriver import ActionChains, Firefox

from modules.browser_object import SmartWindow
from modules.visual_baseline import VisualBaseline

# Only macOS baselines have been captured so far.
pytestmark = pytest.mark.skipif(
    platform.system() != "Darwin",
    reason="Visual baselines have only been captured for macOS so far.",
)


@pytest.fixture()
def test_case():
    return "4028091"


def test_switcher_button_nova_styling(
    driver: Firefox, smart_window: SmartWindow, visual_baseline: VisualBaseline
):
    """
    C4028091 - The Smart Window Switcher is updated to the new NOVA styling
    """
    smart_window.activate_smart_window()

    with driver.context(driver.CONTEXT_CHROME):
        button = smart_window.get_element("window-switcher-button")

        # Resting state against the NOVA reference. Measured byte-identical
        # across three Firefox launches, so the default tolerance is generous.
        visual_baseline.expect_matches(button, "switcher-button-resting")

        # Hovered and pressed must look different from resting, or the case's
        # "changes its state when hovered or pressed" is unverified. Asserting a
        # difference rather than a second reference keeps one image to maintain
        # and still fails if the states stop being distinct.
        ActionChains(driver).move_to_element(button).perform()
        visual_baseline.expect_differs(button, "switcher-button-resting")

        smart_window.open_window_switcher()
        smart_window.element_visible("window-switcher-view")
        visual_baseline.expect_differs(button, "switcher-button-resting")
