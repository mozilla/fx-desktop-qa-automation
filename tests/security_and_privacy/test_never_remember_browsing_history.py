# import logging
import pytest

# from time import sleep
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi, TabBar

# from modules.page_object_about_prefs import AboutPrefs
# from modules.util import Utilities

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
    return [("browser.privatebrowsing.autostart", True)]


# def test_never_remember_browsing_history_settings(driver: Firefox):
#     """
#     C102381.1: Ensure that setting the browser to never remember history has the correct configurations in about:preferences
#     """
#     # about_prefs = AboutPrefs(driver, category="privacy").open()
#     pass


def test_never_remember_browsing_history_from_panel(driver: Firefox):
    """
    C102381.2: Ensure that setting the browser to never remember history does not actually save any history
    """
    panel_ui = PanelUi(driver).open()
    tabs = TabBar(driver)
    # util = Utilities()

    num_tabs = 6

    # open some tabs
    for i in range(num_tabs):
        driver.get(links[i])
        tabs.new_tab_by_button()
        tabs.switch_to_new_tab()

    # close the first 6 tabs
    with driver.context(driver.CONTEXT_CHROME):
        x_icon = tabs.get_element("tab-x-icon", multiple=True)
        for i in range(num_tabs):
            x_icon[i].click()

    panel_ui.open_panel_menu()

    # go into the history tab
    with driver.context(driver.CONTEXT_CHROME):
        panel_ui.get_element("panel-ui-history").click()

        # check for history
        recently_visited_container = panel_ui.get_element(
            "panel-ui-history-recent-history-container"
        )
        recently_visited_items = panel_ui.get_element(
            "panel-ui-history-recent-history-item",
            multiple=True,
            parent_element=recently_visited_container,
        )

        # ensure no actual items are there
        assert len(recently_visited_items) == 1
        assert recently_visited_items[0].get_attribute("label") == "(Empty)"
