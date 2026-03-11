import pytest
from selenium.webdriver import Firefox

from modules.browser_object_sidebar import Sidebar
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "2639190"


@pytest.fixture()
def add_to_prefs_list():
    return [("sidebar.revamp", False)]


def test_toggle_sidebar_via_toolbar_button(driver: Firefox):
    """
    C2639190 - Verify the sidebar can be opened and closed using the toolbar button after enabling Show Sidebar from
    about:preferences.
    """
    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="general")
    sidebar = Sidebar(driver)

    # Enable Show Sidebar from about:preferences (note that enabling the sidebar auto-opens it)
    about_prefs.open()
    about_prefs.enable_show_sidebar()

    # Verify that the sidebar opened automatically after enabling Show Sidebar
    sidebar.expect_sidebar_open()

    # Click the Sidebar button and verify that the sidebar is closed
    sidebar.click_sidebar_button()
    sidebar.expect_sidebar_closed()

    # Click the Sidebar button and verify that the sidebar is open
    sidebar.click_sidebar_button()
    sidebar.expect_sidebar_open()
