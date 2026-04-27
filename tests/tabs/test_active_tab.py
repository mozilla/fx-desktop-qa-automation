import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar

NUM_TABS = 5


@pytest.fixture()
def test_case():
    return "134646"


def test_active_tab(driver: Firefox):
    """
    C134646, ensures that the selected tab is highlighted
    """

    # Instantiate objects
    tabs = TabBar(driver)

    # Open 5 tabs
    for i in range(NUM_TABS):
        tabs.new_tab_by_button()

    # Go through all the tabs and ensure the focus is correct
    tabs.verify_tab_focus_cycle(NUM_TABS)
