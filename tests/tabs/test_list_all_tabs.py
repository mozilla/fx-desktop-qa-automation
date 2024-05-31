import logging

from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import TabBar
from modules.util import BrowserActions


def test_list_all_tabs(driver: Firefox, screenshot):
    # C134655
    tabs = TabBar(driver).open()
    ba = BrowserActions(driver)
    driver.get("about:blank")
    for _ in range(15):
        tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[13])
    target_tab = tabs.get_tab(14)
    driver.get("about:robots")
    driver.switch_to.window(driver.window_handles[0])
    assert tabs.get_tab_title(target_tab).startswith("Gort")

    # Check that you can scroll the tab out of view
    for _ in range(12):
        tabs.scroll_tabs(tabs.SCROLL_DIRECTION.LEFT)

    with driver.context(driver.CONTEXT_CHROME):
        assert target_tab.location["x"] > driver.get_window_size()["width"]

    # Check that you can scroll the tab back into view
    for _ in range(5):
        tabs.scroll_tabs(tabs.SCROLL_DIRECTION.RIGHT)

    with driver.context(driver.CONTEXT_CHROME):
        assert target_tab.location["x"] < driver.get_window_size()["width"]

        target_tab.click()

        tabs.click_list_all_tabs()
        with open("3.html", "w") as fh:
            fh.write(driver.page_source)
