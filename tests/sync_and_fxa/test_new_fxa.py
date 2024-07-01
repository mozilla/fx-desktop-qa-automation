from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.page_object import GenericPage


@pytest.fixture()
def fxa_env():
    return "stage"


def test_sync_button_reroute(driver: Firefox, fxa_url: str):
    panel_ui = PanelUi(driver)
    page = GenericPage(driver, url="")
    panel_ui.open_panel_menu()
    panel_ui.click_sync_sign_in_button()
    page.url_contains(fxa_url)
