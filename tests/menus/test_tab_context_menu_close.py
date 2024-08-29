import logging

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import (
    HyperlinkContextMenu,
    Navigation,
    TabBar,
    TabContextMenu,
)
from modules.page_object import ExamplePage


@pytest.fixture()
def test_case():
    return "2264627"


links = [
    "about:about",
    "about:addons",
    "about:cache",
    "about:config",
]


def test_close_multiple_tabs_to_left(driver: Firefox):
    """
    C2264627.3.2: close multiple tabs actions (close all the left)
    """
    tabs = TabBar(driver).open()
    tab_context_menu = TabContextMenu(driver)

    tabs_to_open = 4

    # open some tabs
    for i in range(tabs_to_open):
        driver.get(links[i])
        tabs.new_tab_by_button()
        driver.switch_to.window(driver.window_handles[i + 1])

    # close all tabs left of the last tab
    last_tab = tabs.get_tab(tabs_to_open + 1)
    tabs.context_click(last_tab)
    tab_context_menu.click_context_item("context-menu-close-multiple-tabs")

    tab_context_menu.click_and_hide_menu("context-menu-close-multiple-tabs-to-left")

    # Click-and-hide won't hide the parent popup
    tabs.hide_popup("tabContextMenu")

    # verify number of tabs
    logging.info("Trying to verify only 1 tab remains.")
    tabs.wait_for_num_tabs(1)


def test_close_multiple_tabs_other_tabs(driver: Firefox):
    """
    C2264627.3.3: close multiple tabs actions (close all the left)
    """
    tabs = TabBar(driver)
    tab_context_menu = TabContextMenu(driver)

    tabs_to_open = 4

    # open some tabs
    for i in range(tabs_to_open):
        driver.get(links[i])
        tabs.new_tab_by_button()
        driver.switch_to.window(driver.window_handles[i + 1])

    # grab second tab and close all other tabs using the context menu
    second_tab = tabs.get_tab(2)
    tabs.context_click(second_tab)
    tab_context_menu.click_and_hide_menu("context-menu-close-multiple-tabs")

    tabs.context_click(second_tab)
    tab_context_menu.click_and_hide_menu("context-menu-close-multiple-tabs-other-tabs")

    # Click-and-hide won't hide the parent popup
    tabs.hide_popup("tabContextMenu")

    # verify the number of tabs
    logging.info("Trying to verify only 1 tab remains.")
    tabs.wait_for_num_tabs(1)


def test_copy_link(driver: Firefox):
    """
    C2264627.4: Copy the link and verify it was copied
    """
    nav = Navigation(driver)
    hyperlink_context = HyperlinkContextMenu(driver)
    tabs = TabBar(driver)
    example = ExamplePage(driver).open()

    # right click the hyperlink
    example.context_click("more-information")

    # click on the open in new window option
    hyperlink_context.click_and_hide_menu("context-menu-copy-link")

    # open a new tab
    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[1])

    # # context click and paste
    search_bar = nav.get_awesome_bar()
    nav.context_click(search_bar)

    # paste and go
    nav.click_and_hide_menu("context-menu-paste-and-go")

    example.title_contains(example.MORE_INFO_TITLE)
    example.url_contains(example.MORE_INFO_URL)
