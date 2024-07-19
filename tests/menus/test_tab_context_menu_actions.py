import logging

from selenium.webdriver import Firefox

from modules.browser_object import TabBar, TabContextMenu

links = [
    "about:about",
    "about:addons",
    "about:cache",
    "about:config",
]


def test_duplicate_tab(driver: Firefox):
    """
    C2637624.1: duplicate tab
    """
    tabs = TabBar(driver).open()
    tab_context_menu = TabContextMenu(driver)

    tabs_to_open = 4

    # open some tabs
    for i in range(tabs_to_open):
        driver.get(links[i])
        tabs.new_tab_by_button()
        driver.switch_to.window(driver.window_handles[i + 1])

    # context click
    first_tab = tabs.get_tab(1)
    tabs.context_click(first_tab)
    tab_context_menu.click_and_hide_menu("context-menu-duplicate-tab")

    # get the current tab and assert the url
    driver.switch_to.window(driver.window_handles[tabs_to_open + 1])
    current_page = driver.current_url
    assert current_page == links[0]


def test_close_multiple_tabs_to_right(driver: Firefox):
    """
    C2637624.3.1: close multiple tabs actions (close all the right)
    """
    tabs = TabBar(driver).open()
    tab_context_menu = TabContextMenu(driver)

    tabs_to_open = 4

    # open some tabs
    for i in range(tabs_to_open):
        driver.get(links[i])
        tabs.new_tab_by_button()
        driver.switch_to.window(driver.window_handles[i + 1])

    first_tab = tabs.get_tab(1)
    tabs.context_click(first_tab)
    tab_context_menu.click_context_item("context-menu-close-multiple-tabs")

    tab_context_menu.click_and_hide_menu("context-menu-close-multiple-tabs-to-right")

    # Click-and-hide won't hide the parent popup
    tabs.hide_popup("tabContextMenu")

    logging.info("Trying to verify only 1 tab remains.")
    tabs.wait_for_num_tabs(1)


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
