import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi, Sidebar


@pytest.fixture()
def test_case():
    return "2652545"


def test_sidebar_enabled_in_private_window(driver: Firefox):
    """
    C2652545 - Verify that the sidebar button is displayed in the toolbar in a private window and that the sidebar
    can be opened
    """
    # Instantiate object
    sidebar = Sidebar(driver)
    panel_ui = PanelUi(driver)

    # Open Private Window
    panel_ui.open_and_switch_to_new_window("private")

    # Verify that the Sidebar button is present in the toolbar
    sidebar.element_visible("sidebar-button")

    # Click the Sidebar button and verify that the sidebar is open
    sidebar.click_sidebar_button()
    sidebar.expect_sidebar_open()
