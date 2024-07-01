from time import sleep

from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.page_object import GenericPage


def test_sync_button_reroute(driver: Firefox):
    panel_ui = PanelUi(driver)
    page = GenericPage(driver, url="")
    panel_ui.open_panel_menu()
    panel_ui.click_sync_sign_in_button()
    page.url_contains("accounts.stage.mozaws")
