import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi, TabBar
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "118802"


@pytest.fixture()
def use_profile():
    return "theme_change"


ETSY_URL = "https://www.etsy.com/"


def test_the_website_opened_in_new_tab_is_present_in_history_menu(driver: Firefox):
    """
    C118802 - Verify that the website opened in new tab is displayed in Hamburger Menu, History section, on top of the
    list
    """
    # Instantiate objects
    tabs = TabBar(driver)
    page = GenericPage(driver, url=ETSY_URL)
    panel = PanelUi(driver)

    # Open a new tab, switch to it and verify is the url contains the desired domain
    tabs.open_web_page_in_new_tab(page, 2)
    page.url_contains("etsy")

    # Verify Etsy is present in the Hamburger Menu, History section and is on top of the list as the most recent
    # website visited
    panel.open_history_menu()
    panel.expect_element_attribute_contains("recent-history-content", "value", "Etsy")
