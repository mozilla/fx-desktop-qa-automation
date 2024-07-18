import logging

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation
from modules.page_object import ExamplePage, GenericPage


def test_open_link_in_private_window(driver: Firefox):
    """C101662 - Links can be successfully opened in a Private Browsing session"""
    example = ExamplePage(driver)
    example.open()
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)

    example.context_click("more-information")
    context_menu.click_and_hide_menu("context-menu-open-link-in-new-private-window")

    nav.wait_for_num_windows(2)
    nav.switch_to_new_window()
    with driver.context(driver.CONTEXT_CHROME):
        nav.title_contains("Private Browsing")
    example.title_contains(example.MORE_INFO_TITLE)
    example.url_contains(example.MORE_INFO_URL)
