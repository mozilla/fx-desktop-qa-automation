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
    with driver.context(driver.CONTEXT_CHROME):
        tabs.actions.context_click(first_tab).perform()
        tab_item = tab_context_menu.get_context_item("context-menu-pin-tab")
        tab_item.click()

        # grab the attribute pinned
        pinned_attribute = first_tab.get_attribute("pinned")
        logging.info(f"The pinned attribute is: {pinned_attribute}")
        assert pinned_attribute == "true"

        # ensuring all the other tabs are not pinned
        for i in range(2, num_tabs + 2):
            tab = tabs.get_tab(i)
            pinned_attribute = tab.get_attribute("pinned")
            logging.info(f"The pinned attribute is: {pinned_attribute}")
            assert pinned_attribute == "false"
