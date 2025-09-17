import logging

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "118807"


@pytest.fixture()
def use_profile():
    return "theme_change"


def test_open_websites_from_history(driver: Firefox):
    """
    C118807: Verify that the user can open any random website from Hamburger Menu, History section
    """
    # Instantiate object
    panel = PanelUi(driver)

    # Open History section from Hamburger Menu and get a random entry from browser history
    panel.open_history_menu()
    result = panel.get_random_history_entry()

    # Skip test if no history entries are available
    if result is None:
        logging.info("Test skipped: No history available")
        return

    # Extract URL and page title from the selected history entry
    url, label = result

    # Navigate to the selected page and verify it loads correctly
    page = GenericPage(driver, url=url)
    page.open()
    page.url_contains(url)
    page.title_contains(label)
