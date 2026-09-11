"""
C3309854 - Open a New Classic Window from the Smart Window
Verify the hamburger menu in a Smart Window offers "New Classic Window" in
place of "New Smart Window", and that it opens a Classic Window.
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.browser_object_smart_window import SmartWindow


@pytest.fixture()
def test_case():
    return "3309854"


def test_open_classic_window_from_smart_window(
    driver: Firefox, active_smart_window: SmartWindow
):
    """
    C3309854 - Open a New Classic Window from the Smart Window
    """
    panel_ui = PanelUi(driver)
    panel_ui.open_panel_menu()

    # A Smart Window swaps the "New Smart Window" entry for "New Classic Window".
    panel_ui.element_not_visible("panel-ui-new-smart-window")
    panel_ui.element_visible("panel-ui-new-classic-window")

    existing_handles = set(driver.window_handles)
    panel_ui.click_on("panel-ui-new-classic-window")

    new_handle = active_smart_window.wait_for_new_window(existing_handles)
    driver.switch_to.window(new_handle)

    new_window = SmartWindow(driver)
    new_window.is_not_private()  # waits and asserts; raises on timeout

    # The window is briefly created in the Smart state before being toggled to
    # Classic, so poll for the settled state rather than reading it once.
    new_window.expect_smart_window_active(False)
