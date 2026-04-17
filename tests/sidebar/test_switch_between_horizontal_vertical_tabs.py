import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Sidebar


@pytest.fixture()
def test_case():
    return "2652980"


@pytest.fixture()
def add_to_prefs_list():
    return [("sidebar.revamp", True), ("sidebar.verticalTabs", False)]


def test_switch_between_horizontal_vertical_tabs(driver: Firefox):
    """
    C2652980 - Verify that the Customize sidebar gear icon displays the Vertical tabs checkbox under
    Sidebar settings, and checking it switches the tabs to Vertical in the Sidebar.
    """
    # Instantiate object
    sidebar = Sidebar(driver)

    # Open the sidebar, click the Customize gear icon and verify the Vertical tabs option is displayed
    sidebar.click_sidebar_button()
    sidebar.expect_sidebar_open()
    sidebar.click_customize_sidebar()
    sidebar.expect_vertical_tabs_checkbox_visible()

    # Check the Vertical tabs option and verify tabs are switched to Vertical in the Sidebar
    sidebar.click_vertical_tabs_checkbox()
    sidebar.expect_vertical_tabs_active()

    # Uncheck the Vertical tabs option and verify tabs are switched back to Horizontal
    sidebar.click_vertical_tabs_checkbox()
    sidebar.expect_horizontal_tabs_active()
