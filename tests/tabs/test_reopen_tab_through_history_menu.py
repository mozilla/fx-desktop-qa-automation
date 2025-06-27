import logging
from platform import system

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi, TabBar


@pytest.fixture()
def test_case():
    return "134650"


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


@pytest.mark.skipif(
    system().lower().startswith("linux"), reason="Currently unstable in linux"
)
def test_reopen_tab_through_history_menu(driver: Firefox):
    """C134650 - Verify that the recently closed tab can be reopened from the history menu"""
    # open 6 tabs
    tabs = TabBar(driver)
    panel = PanelUi(driver)
    num_tabs = 6

    for i in range(num_tabs):
        driver.get(links[i])
        tabs.new_tab_by_button()
        driver.switch_to.window(driver.window_handles[i + 1])

    # close the first 6 tabs
    for i in range(num_tabs):
        tabs.close_tab(tabs.get_tab(num_tabs - i))

    # open menu bar and reopen recently closed tabs
    panel.open()
    panel.reopen_recently_closed_tabs()

    # go through all the tabs and ensure they were the ones that were opened previously
    for i in range(num_tabs):
        driver.switch_to.window(driver.window_handles[i + 1])
        current_page = driver.current_url
        logging.info(f"The current URL is: {current_page}")
        assert current_page in link_set
