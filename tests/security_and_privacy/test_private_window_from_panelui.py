import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.page_object import AboutPrivatebrowsing


@pytest.fixture()
def test_case():
    return "101660"


def test_private_window_from_panelui(driver: Firefox):
    """C101660 - Private Browsing can be successfully opened via the Hamburger menu"""
    panelui = PanelUi(driver)
    panelui.open_panel_menu()
    panelui.select_panel_setting("new-private-window-option")
    panelui.switch_to_new_window()
    AboutPrivatebrowsing(driver).wait_for_page_to_load()
