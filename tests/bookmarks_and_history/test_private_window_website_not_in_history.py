import pytest
from selenium.webdriver import Firefox

from modules.browser_object_panel_ui import PanelUi
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "118806"


YOUTUBE_URL = "https://www.youtube.com/"


def test_opened_website_in_private_window_not_captured_in_history_list(driver: Firefox):
    """
    C118806 - Verify that opened websites in a New Private Window will not be displayed in the Hamburger History submenu
    """
    # Instantiate objects
    panel = PanelUi(driver)
    page = GenericPage(driver, url=YOUTUBE_URL)

    # Open the desired webpage in a new Private window
    panel.open_and_switch_to_new_window("private")
    page.open()

    # Verify that the webpage opened in Private window is not listed in History
    panel.open_history_menu()
    panel.confirm_history_clear()
