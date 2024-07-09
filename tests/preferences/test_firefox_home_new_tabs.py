from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.page_object import AboutNewtab, AboutPrefs


def test_firefox_home_new_tab(driver: Firefox):
    """
    C161472: setting the default new window to be Firefox Home
    """
    # instantiate objs
    about_prefs = AboutPrefs(driver, category="home").open()
    tabs = TabBar(driver)
    about_new_tab = AboutNewtab(driver)

    # click the dropdown
    drop_down = about_prefs.get_element("home-new-tabs-dropdown")
    dropdown = about_prefs.Dropdown(page=about_prefs, root=drop_down)
    dropdown.select_option("Firefox Home (Default)")

    # make sure that the option was selected correctly
    assert drop_down.get_attribute("label") == "Firefox Home (Default)"
    tabs.new_tab_by_button()

    # wait for the number of tabs and switch
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[-1])

    # make sure we are on the correct new tab page
    assert about_new_tab.get_element("body-logo") is not None
