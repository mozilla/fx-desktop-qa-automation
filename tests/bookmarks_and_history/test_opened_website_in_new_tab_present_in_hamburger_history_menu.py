import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi, TabBar
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "118802"


@pytest.fixture()
def use_profile():
    return "theme_change"


WIKIPEDIA_URL = "https://www.wikipedia.org/"


def test_the_website_opened_in_new_tab_is_present_in_history_menu(driver: Firefox):
    """
    C118802 - Verify that the website opened in new tab is displayed in Hamburger Menu, History section, on top of the
    list
    """
    # Instantiate objects
    tabs = TabBar(driver)
    page = GenericPage(driver, url=WIKIPEDIA_URL)
    panel = PanelUi(driver)

    # Open a desired webpage in a new tab
    tabs.open_web_page_in_new_tab(page, 2)
    page.url_contains("wikipedia")

    # Verify the opened webpage from last step is present in the Hamburger Menu, History section and is on top of the
    # list as the most recent website visited
    panel.open_history_menu()
    panel.verify_most_recent_history_item("Wikipedia")
