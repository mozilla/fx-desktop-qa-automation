"""
C3313457 - Reach History from the Hamburger menu
Verify a Smart Window's hamburger menu shows both History and the Chats entry
beside it, and that History opens its subview.
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi, SmartWindow


@pytest.fixture()
def test_case():
    return "3313457"


def test_history_from_hamburger_menu(driver: Firefox, active_smart_window: SmartWindow):
    """
    C3313457 - Reach History from the Hamburger menu
    """
    panel_ui = PanelUi(driver)
    panel_ui.open_panel_menu()

    # Chats is in the main view, not the History subview, so assert it before
    # navigating in. Visibility, not existence: a Classic Window carries the
    # same element with hidden="", and that difference is what makes this a
    # Smart Window test rather than a generic Firefox one.
    panel_ui.element_visible("panel-ui-chats-history")

    # Not open_history_menu(): it calls open_panel_menu(), which clicks
    # unconditionally and would toggle the panel shut.
    panel_ui.click_on("panel-ui-history")
    panel_ui.element_visible("panel-ui-history-view")
    panel_ui.element_visible("panel-ui-history-recent-history-container")
