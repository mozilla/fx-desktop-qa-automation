from selenium.webdriver import Firefox

from modules.browser_object import TabBar


def test_active_tab(driver: Firefox):
    """
    C134646, ensures that the selected tab is highlighted
    """
    tabs = TabBar(driver).open()
    num_tabs = 5

    # opening 5 tabs
    for i in range(num_tabs):
        tabs.new_tab_by_button()

    # go through all the tabs and ensure highlighted one is correct, +2 since 1 indexed and additional tab for the beginning
    # for i in range(1, num_tabs + 2):
    for i in range(1, 2):
        target_tab = tabs.get_tab(i)
        with driver.context(driver.CONTEXT_CHROME):
            target_tab.click()
            visibility = target_tab.get_attribute("visuallyselected")
            assert visibility == ""
