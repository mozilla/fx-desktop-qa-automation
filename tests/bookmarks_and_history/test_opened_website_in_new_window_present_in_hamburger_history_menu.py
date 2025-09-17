import pytest
from selenium.webdriver import Firefox

from modules.browser_object_panel_ui import PanelUi
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "118805"


@pytest.fixture()
def use_profile():
    return "theme_change"


WIKIPEDIA_URL = "https://www.wikipedia.org/"


def test_the_website_opened_in_new_window_is_present_in_history_menu(driver: Firefox):
    """
    C118805 - Verify that the website opened in new window is displayed in Hamburger Menu, History section, on top of the
    list
    """

    # Instantiate objects
    page = GenericPage(driver, url=WIKIPEDIA_URL)
    panel = PanelUi(driver)

    # Open a new window, switch to it and verify is the url contains the desired page name
    panel.open_and_switch_to_new_window("window")
    page.open()
    page.url_contains("wikipedia")

    # Verify Wikipedia is present in the history menu and is on top of the list as the most recent website visited
    panel.open_history_menu()
    panel.verify_most_recent_history_item("Wikipedia")
