from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation, PanelUi, TabBar

VISIT_URL = "about:about"

links = [
    "about:about",
    "about:addons",
    "about:cache",
    "about:config",
    "about:buildconfig",
    "about:robots",
    "about:blank",
]

link_set = set(links)


@pytest.fixture()
def add_prefs():
    return []


def test_undo_close_tab_private_browsing(driver: Firefox):
    """
    C120118: ensure that you can close a tab in private browsing window
    """
    # instantiate objs
    panel_ui = PanelUi(driver)
    nav = Navigation(driver).open()
    tabs = TabBar(driver)

    # open a new private window and open a new tab
    panel_ui.open_private_window()
    tabs.switch_to_new_tab()

    # open a new tab
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()

    # navigate to the URL NOTE: TEMPORARY GET AWESOME BAR PRIVATE. ADD SUPPORT FOR IT IN NAVIGATION
    with driver.context(driver.CONTEXT_CHROME):
        search_bar = nav.get_element("awesome-bar-private")
        search_bar.send_keys(VISIT_URL + Keys.ENTER)
    tabs.wait_for_num_tabs(3)
    # tabs.switch_to_new_tab()
    # for _ in range(100):
    #     print(len(driver.window_handles))
    #     sleep(0.5)

    tabs.close_tab_of_index(0)

    sleep(40)
