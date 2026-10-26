import pytest
from auto_fxui.browser_object import Navigation
from selenium.webdriver import Firefox

WIKIPEDIA_URL = "https://www.wikipedia.org/"


@pytest.fixture()
def test_case():
    return "3895126"


def test_add_to_taskbar_button_is_not_displayed_in_private_windows(driver: Firefox):
    """
    C3895126 - Verify that Add to taskbar button is not displayed in private browsing windows
    """

    # Instantiate objects
    nav = Navigation(driver)

    # Open private browsing window
    nav.open_and_switch_to_new_window("private")
    nav.is_private()
    driver.get(WIKIPEDIA_URL)

    # Verify "Add tab to taskbar" button is not displayed in private window
    nav.element_not_visible("taskbar-tabs-button")
