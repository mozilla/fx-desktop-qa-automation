"""
C3309852 - Open a Smart Window from the Hamburger menu
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi, SmartWindow
from modules.classes.fxa_session import FxaSession
from modules.page_object import FxaHome


@pytest.fixture()
def test_case():
    return "3309852"


def test_open_smart_window_from_hamburger(
    driver: Firefox, create_fxa: FxaSession, smart_window: SmartWindow
):
    """
    C3309852 - Open a Smart Window from the Hamburger menu
    """
    # The entry goes through ensureAIWindowAccess, so signed out it opens a
    # plain window at about:blank rather than a Smart one.
    smart_window.open_smart_window_sign_in()
    fxa = FxaHome(driver)
    fxa.inject_session(create_fxa)
    fxa.continue_with_cached_account()
    smart_window.expect_signed_in()

    # The window turns Smart asynchronously after sign-in resolves.
    smart_window.expect_smart_window_active(True)

    # Back to Classic, the window type that offers "New Smart Window".
    smart_window.switch_to_classic_window()

    panel_ui = PanelUi(driver)
    panel_ui.open_panel_menu()
    panel_ui.element_visible("panel-ui-new-smart-window")

    existing_count = len(driver.window_handles)
    panel_ui.click_on("panel-ui-new-smart-window")
    smart_window.wait_for_num_windows(existing_count + 1)
    smart_window.switch_to_new_window()
    SmartWindow(driver).expect_smart_window_active(True)
