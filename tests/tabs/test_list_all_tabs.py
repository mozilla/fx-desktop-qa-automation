from selenium.webdriver import Firefox

from modules.browser_object import TabBar


def test_list_all_tabs(driver: Firefox):
    # C134655
    tabs = TabBar(driver).open()
    driver.get("about:robots")
    for _ in range(20):
        tabs.new_tab_by_button()
    tabs.click_list_all_tabs()
