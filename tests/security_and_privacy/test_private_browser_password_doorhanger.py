from time import sleep
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi
from modules.page_object import GenericPage, LoginAutofill

def test_no_password_doorhanger_private_browsing(driver: Firefox):
    """
    C101670: Ensure no save password doorhanger shows up and settings are correct
    """
    login_auto_fill = LoginAutofill(driver)
    panel_ui = PanelUi(driver).open()
    nav = Navigation(driver)

    panel_ui.open_private_window()
    nav.switch_to_new_window()

    login_auto_fill.open()
    sleep(5)