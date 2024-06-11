from selenium.webdriver import Firefox

from modules.browser_object import TabBar


def test_active_test(driver: Firefox):
    """
    C134646, ensures that the selected tab is highlighted
    """
    tabs = TabBar(driver).open()
    num_tabs = 5

    # opening 5 tabs
    for i in range(num_tabs):
        tabs.new_tab_by_button()

    # go through all the tabs and ensure highlighted one is correct, +2 since 1 indexed and additional tab for the beginning
    for i in range(1, num_tabs + 2):
        target_tab = tabs.get_tab(i)
        with driver.context(driver.CONTEXT_CHROME):
            target_tab.click()
            tab_color = target_tab.value_of_css_property("color")
            visibility = target_tab.get_attribute("visuallyselected")
            assert visibility == ""
            assert tab_color == "rgb(12, 12, 13)" and tab_color != "rgb(21, 20, 26)"

    # tabs.new_tab_by_button()
    # target_tab = tabs.get_tab(3)
    # with driver.context(driver.CONTEXT_CHROME):
    #     css_properties = driver.execute_script("""
    #         var styles = window.getComputedStyle(arguments[0]);
    #         var styleObject = {};
    #         for (var i = 0; i < styles.length; i++) {
    #             styleObject[styles[i]] = styles.getPropertyValue(styles[i]);
    #         }
    #             return styleObject;
    #         """, target_tab)
    #     print(css_properties)
