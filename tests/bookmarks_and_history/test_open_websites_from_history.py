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

    # Instantiate objects
    panel = PanelUi(driver)
    panel.open_history_menu()

    result = panel.get_random_history_entry()

    if result is None:
        logging.info("Test skipped: No history available")
        return

    # Retrieve a random item from history and its label
    url, label = result

    # Open the corresponding page and verify URL and title match
    page = GenericPage(driver, url=url)
    page.open()
    page.url_contains(url)
    page.title_contains(label)
