from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation
from modules.page_object import ExamplePage


@pytest.fixture()
def test_case():
    return "101662"


def test_open_link_in_private_window(driver: Firefox, nav: Navigation):
    """C101662 - Links can be successfully opened in a Private Browsing session"""
    example = ExamplePage(driver)
    context_menu = ContextMenu(driver)
    example.open()

    sleep(1)
    example.context_click("learn-more")
    sleep(1)
    context_menu.click_and_hide_menu("context-menu-open-link-in-new-private-window")

    nav.switch_to_new_window()
    sleep(1)
    nav.is_private()
    example.title_contains(example.MORE_INFO_TITLE)
    example.url_contains(example.MORE_INFO_URL)
