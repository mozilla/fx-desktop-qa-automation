from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.util import BrowserActions


def test_list_all_tabs(driver: Firefox):
    # C134655
    tabs = TabBar(driver).open()
    ba = BrowserActions(driver)
    driver.get("about:blank")
    for _ in range(30):
        tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[10])
    driver.get("about:robots")
    driver.switch_to.window(driver.window_handles[0])

    tabs.click_list_all_tabs()
