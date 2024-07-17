import logging

from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import TabBar

ROBOT_TAB = 16


def test_list_all_tabs(driver: Firefox, screenshot):
    """
    C134655, check that the List All Tabs button and menu act as expected.
    """
    tabs = TabBar(driver).open()
    driver.get("about:blank")
    for _ in range(17):
        tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[ROBOT_TAB - 1])
    target_tab = tabs.get_tab(ROBOT_TAB)
    driver.get("about:robots")
    with driver.context(driver.CONTEXT_CHROME):
        assert tabs.get_tab_title(target_tab).startswith("Gort")

        target_tab.click()
        tabs.open_all_tabs_list()
        assert tabs.get_text_of_all_tabs_entry(selected=True).startswith("Gort")
        tabs.actions.send_keys(Keys.ESCAPE).perform()

    # Check that you can scroll the tab out of view
    tab_out_of_view = False
    for _ in range(40):
        tabs.scroll_tabs(tabs.SCROLL_DIRECTION.LEFT)
        with driver.context(driver.CONTEXT_CHROME):
            if target_tab.location["x"] > (driver.get_window_size()["width"]):
                logging.info(
                    f"Tab location {target_tab.location['x']} should be greater..."
                )
                logging.info(
                    f"...than window width {driver.get_window_size()['width']}"
                )
                tab_out_of_view = True
                break
    assert tab_out_of_view

    # Check that you can scroll the tab back into view
    for _ in range(5):
        tabs.scroll_tabs(tabs.SCROLL_DIRECTION.RIGHT)

    with driver.context(driver.CONTEXT_CHROME):
        assert target_tab.location["x"] < driver.get_window_size()["width"]

        target_tab.click()

        tabs.open_all_tabs_list()
        assert tabs.get_text_of_all_tabs_entry(selected=True).startswith("Gort")
        tabs.actions.send_keys(Keys.ESCAPE).perform()

    for _ in range(27):
        tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[-1])
    driver.get("about:about")

    entry_out_of_view = False
    with driver.context(driver.CONTEXT_CHROME):
        tabs.open_all_tabs_list()
        for _ in range(3):
            all_tabs_menu = tabs.get_element("all-tabs-menu")
            tabs.scroll_on_all_tabs_menu(down=False)
            about_about_location = tabs.get_location_of_all_tabs_entry(selected=True)
            all_tabs_menu = tabs.get_element("all-tabs-menu")
            all_tabs_menu_bottom = (
                all_tabs_menu.location["y"] + all_tabs_menu.size["height"]
            )
            if about_about_location["y"] > all_tabs_menu_bottom:
                entry_out_of_view = True
        assert entry_out_of_view, f"Entry location {about_about_location['y']} should be greater than {all_tabs_menu.size['height']}"
