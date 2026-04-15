import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, Sidebar


@pytest.fixture()
def test_case():
    return "2947565"


@pytest.fixture()
def add_to_prefs_list():
    return [("sidebar.expandOnHover", True)]


def test_switching_to_horizontal_tabs_disables_expand_on_hover(driver: Firefox):
    """
    C2947565 - Verify that switching to horizontal tabs, the expand/collapse by hover option is disabled.
    """
    # Instantiate objects
    sidebar = Sidebar(driver)
    nav = Navigation(driver)

    # Enable vertical tabs via toolbar context menu
    nav.toggle_vertical_tabs()

    # Open the Customize Sidebar panel via the gear icon in the sidebar strip
    sidebar.click_customize_sidebar()

    # Uncheck Vertical Tabs to switch back to horizontal tabs
    sidebar.click_vertical_tabs_checkbox()
    sidebar.expect_horizontal_tabs_active()

    # Verify the expand/collapse on hover option is disabled automatically
    sidebar.expect_expand_on_hover_disabled()
