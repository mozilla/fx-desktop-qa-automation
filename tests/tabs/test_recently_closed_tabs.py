import logging

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi, TabBar


@pytest.fixture()
def test_case():
    return "134648"


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


def test_recently_closed_tabs(driver: Firefox):
    """C134648 - Verify that the recently closed tab can be reopened from the context menu"""
    # open 6 tabs
    tabs = TabBar(driver)
    panel = PanelUi(driver)
    num_tabs = 6

    for i in range(num_tabs):
        driver.get(links[i])
        tabs.new_tab_by_button()
        driver.switch_to.window(driver.window_handles[i + 1])

    # close the first 6 tabs
    with driver.context(driver.CONTEXT_CHROME):
        x_icon = tabs.get_element("tab-x-icon", multiple=True)
        for i in range(num_tabs):
            x_icon[i].click()

    # open menu bar and reopen recently closed tabs
    panel.open()
    panel.open_panel_menu()
    with driver.context(driver.CONTEXT_CHROME):
        panel.get_element("panel-ui-history").click()

        panel.element_clickable("panel-ui-history-recently-closed")
        panel.get_element("panel-ui-history-recently-closed").click()

        panel.element_clickable("panel-ui-history-recently-closed-reopen-tabs")
        panel.get_element("panel-ui-history-recently-closed-reopen-tabs").click()

    # go through all the tabs and ensure they were the ones that were opened previously
    for i in range(num_tabs):
        driver.switch_to.window(driver.window_handles[i + 1])
        current_page = driver.current_url
        logging.info(f"The current URL is: {current_page}")
        assert current_page in link_set
