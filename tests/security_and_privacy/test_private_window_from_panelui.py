from time import sleep

from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.page_object import AboutPrivatebrowsing


def test_private_window_from_panelui(driver: Firefox):
    panelui = PanelUi(driver).open_panel_menu()
    panelui.select_panel_setting("new-private-window-option")
    panelui.wait_for_num_windows(2)
    panelui.switch_to_new_tab()
    private = AboutPrivatebrowsing(driver).wait_for_page_to_load()
