"""
C3309853 - Open a New Private Window from the Smart Window
Verify a Private Browsing window can be opened from a Smart Window, and that
it is neither private-plus-smart nor missing its private state.
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.browser_object_smart_window import SmartWindow


@pytest.fixture()
def test_case():
    return "3309853"


def test_open_private_window_from_smart_window(
    driver: Firefox, active_smart_window: SmartWindow
):
    """
    C3309853 - Open a New Private Window from the Smart Window
    """
    panel_ui = PanelUi(driver)
    smart_handle = driver.current_window_handle
    existing_handles = set(driver.window_handles)

    panel_ui.open_panel_menu()
    panel_ui.element_visible("panel-ui-new-private-window")
    panel_ui.click_on("panel-ui-new-private-window")

    new_handle = active_smart_window.wait_for_new_window(existing_handles)
    driver.switch_to.window(new_handle)

    private_window = SmartWindow(driver)
    private_window.is_private()  # waits and asserts; raises on timeout

    # Private Browsing never carries the Smart Window state.
    private_window.expect_smart_window_active(False)
    assert not private_window.switcher_button_available()

    # Positive control: the window we opened it from is still a Smart Window,
    # so the assertions above reflect Private Browsing being exempt rather
    # than Smart Window being unavailable in this profile.
    driver.switch_to.window(smart_handle)
    active_smart_window.expect_smart_window_active(True)
    assert active_smart_window.switcher_button_available()
