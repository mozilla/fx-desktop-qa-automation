import logging

from selenium.webdriver import Firefox

from modules.browser_object import TabBar, TabContextMenu


def test_pin_tab(driver: Firefox):
    """
    C134722, ensures that tabs can be pinned
    """
    tabs = TabBar(driver).open()
    tab_context_menu = TabContextMenu(driver)

    num_tabs = 5

    # opening some tabs
    for _ in range(num_tabs):
        tabs.new_tab_by_button()

    # pin the 1st tab
    first_tab = tabs.get_tab(1)
    tabs.context_click(first_tab)
    tab_context_menu.click_and_hide_menu("context-menu-pin-tab")

    assert tabs.is_pinned(first_tab)

    # ensuring all the other tabs are not pinned
    for i in range(2, num_tabs + 2):
        tab = tabs.get_tab(i)
        assert not tabs.is_pinned(tab)

    # unpinning the tab and ensuring it is no longer pinned
    tabs.context_click(first_tab)
    tab_context_menu.click_and_hide_menu("context-menu-unpin-tab")

    assert not tabs.is_pinned(first_tab)
