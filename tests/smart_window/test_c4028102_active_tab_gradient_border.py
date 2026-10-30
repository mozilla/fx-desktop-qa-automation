"""
C4028102 - Active tab gradient border
Verify the active tab renders the NOVA gradient border that marks it selected,
and that an inactive tab does not.
"""

import platform

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from auto_fxui.browser_object import SmartWindow
from auto_fxui.visual_baseline import VisualBaseline

pytestmark = pytest.mark.skipif(
    platform.system() != "Darwin",
    reason="Visual baselines have only been captured for macOS so far.",
)

# XUL quirk: tab[selected] matches, .tabbrowser-tab[selected='true'] does not.
SELECTED_TAB = "tab[selected]"
ANY_TAB = "tab"


@pytest.fixture()
def test_case():
    return "4028102"


def test_active_tab_gradient_border(
    driver: Firefox, smart_window: SmartWindow, visual_baseline: VisualBaseline
):
    """
    C4028102 - Active tab gradient border
    """
    smart_window.activate_smart_window()

    with driver.context(driver.CONTEXT_CHROME):
        active = driver.find_element(By.CSS_SELECTOR, SELECTED_TAB)
        visual_baseline.expect_matches(active, "active-tab")

        # Open a second tab so the first becomes inactive, then check it no
        # longer carries the border. Without this the test would pass even if
        # every tab were drawn with the gradient.
        driver.find_element(By.ID, "tabs-newtab-button").click()
        smart_window.expect(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, ANY_TAB)) == 2
        )
        inactive = [
            tab
            for tab in driver.find_elements(By.CSS_SELECTOR, ANY_TAB)
            if not tab.get_attribute("selected")
        ]
        assert len(inactive) == 1, f"expected one inactive tab, got {len(inactive)}"
        visual_baseline.expect_differs(inactive[0], "active-tab")
