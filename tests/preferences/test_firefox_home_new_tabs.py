from time import sleep

from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.page_object import AboutNewtab, AboutPrefs


def test_firefox_home_new_tab(driver: Firefox):
    """
    C161472: setting the default new window to be Firefox Home
    """
    about_prefs = AboutPrefs(driver, category="home").open()
    tabs = TabBar(driver)
    about_new_tab = AboutNewtab(driver)

    drop_down = about_prefs.get_element("home-new-tabs-dropdown")
    drop_down.click()

    home_option = about_prefs.get_element(
        "home-new-tabs-dropdown-option-default", parent_element=drop_down
    )
    home_option.click()

    assert drop_down.get_attribute("label") == "Firefox Home (Default)"
    tabs.new_tab_by_button()

    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[-1])

    assert about_new_tab.get_element("body-logo") is not None
