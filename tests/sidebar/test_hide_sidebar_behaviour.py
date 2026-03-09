import pytest
from selenium.webdriver import Firefox

from modules.browser_object_sidebar import Sidebar


@pytest.fixture()
def test_case():
    return "2651719"


def test_sidebar_is_hidden_when_hide_sidebar_option_is_selected(driver: Firefox):
    """
    C2651719 - Verify that the sidebar is hidden when the Hide Sidebar option is selected
    from the sidebar context menu.
    """
    # Instantiate object
    sidebar = Sidebar(driver)

    # Open the Firefox Sidebar from the Toolbar button
    sidebar.click_sidebar_button()
    sidebar.expect_sidebar_open()

    # Right-click on the sidebar and select Hide Sidebar option
    sidebar.hide_sidebar_via_context_menu()

    # Sidebar is hidden when the option is selected
    sidebar.element_not_visible("sidebar-main")
