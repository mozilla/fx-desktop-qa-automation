import pytest
from selenium.webdriver import Firefox

from modules.browser_object_panel_ui import PanelUi
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "118800"


@pytest.fixture()
def use_profile():
    return "theme_change"


WIKIPEDIA_URL = "https://www.wikipedia.org/"


def test_the_most_recent_website_is_present_in_history_menu(driver: Firefox):
    """
    C118800 - Verify that the most recently opened website is displayed in Hamburger Menu, History section, on top of the
    list
    """
    # Instantiate objects
    page = GenericPage(driver, url=WIKIPEDIA_URL)
    panel = PanelUi(driver)

    # Open the desired webpage
    page.open()

    # Verify Wikipedia is present in the history menu and is on top of the list as the most recent website visited
    panel.open_history_menu()
    panel.verify_most_recent_history_item("Wikipedia")
