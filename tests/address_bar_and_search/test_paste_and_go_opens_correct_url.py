from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_context_menu import ContextMenu
from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage

URL_TO_COPY = "https://bug1320502.bmoattachments.org/attachment.cgi?id=8814655"
URL = "https://developer.mozilla.org"


@pytest.fixture()
def test_case():
    return "3028883"


def test_paste_and_go_opens_correct_url(driver: Firefox, pyperclip=None):
    """
    C3028883 - "Paste and Go" opens the right URL
    """

    # Instantiate objects
    nav = Navigation(driver)
    page = GenericPage(driver, url=URL_TO_COPY)
    context_menu = ContextMenu(driver)

    # Copy the link
    page.open()
    test = page.get_element("url-to-copy").get_attribute("value")
    print(test)

    # Open a new tab and right click in the Address bar and choose Paste and Go
    nav.open_and_switch_to_new_window("tab")
    nav.get_awesome_bar()
    nav.click_and_hide_menu("context-menu-paste-and-go")
    sleep(5)

    # Check that the page is displayed
