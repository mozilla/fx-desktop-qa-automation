import logging

from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.util import BrowserActions


def test_list_all_tabs(driver: Firefox):
    # C134655
    tabs = TabBar(driver).open()
    ba = BrowserActions(driver)
    driver.get("about:blank")
    for _ in range(15):
        tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[10])
    driver.get("about:robots")
    driver.switch_to.window(driver.window_handles[0])
    for n in range(1, 13):
        logging.info(tabs.get_tab_title(tabs.get_tab(n)))
    assert tabs.get_tab_title(tabs.get_tab(11)).startswith("Gort")
    for _ in range(20):
        tabs.scroll_tabs(tabs.SCROLL_DIRECTION.LEFT)

    assert tabs.get_tab_title(tabs.get_tab(11)).startswith("Gort")

    tabs.click_list_all_tabs()
