import pytest
from selenium.webdriver import Firefox

from modules.browser_object_sidebar import Sidebar


@pytest.fixture()
def test_case():
    return "2639191"


def test_sidebar_button_always_displayed_on_fresh_profile(driver: Firefox):
    """
    C2639191 - Verify that the sidebar button is displayed in the toolbar on a fresh profile
    """
    # Instantiate object
    sidebar = Sidebar(driver)

    # Verify that the Sidebar button is present in the toolbar
    sidebar.element_visible("sidebar-button")
