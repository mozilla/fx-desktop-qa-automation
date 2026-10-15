import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Sidebar


@pytest.fixture()
def test_case():
    return "2639190"


def test_toggle_sidebar_via_toolbar_button(driver: Firefox):
    """
    C2639190 - Verify the sidebar can be opened and closed using the toolbar button
    """
    # Instantiate objects
    sidebar = Sidebar(driver)

    # Click the Sidebar button and verify that the sidebar is open
    sidebar.click_sidebar_button()
    sidebar.expect_sidebar_open()

    # Click the Sidebar button and verify that the sidebar is closed
    sidebar.click_sidebar_button()
    sidebar.expect_sidebar_closed()
