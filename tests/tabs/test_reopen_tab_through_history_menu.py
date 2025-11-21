import logging

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi, TabBar


@pytest.fixture()
def test_case():
    return "134650"


LINKS = [
    "about:about",
    "about:addons",
    "about:cache",
    "about:config",
    "about:buildconfig",
    "about:robots",
    "about:blank",
]

LINK_SET = set(LINKS)
NUM_TABS = 6


# This test is unstable in Linux Taskcluster for now
def test_reopen_tab_through_history_menu(driver: Firefox):
    """C134650 - Verify that the recently closed tab can be reopened from the history menu"""

    # Instantiate objects
    tabs = TabBar(driver)
    panel = PanelUi(driver)

    # open 6 tabs
    for i in range(NUM_TABS):
        driver.get(LINKS[i])
        tabs.new_tab_by_button()
        driver.switch_to.window(driver.window_handles[i + 1])

    # close the first 6 tabs
    for i in range(NUM_TABS):
        tabs.close_tab(tabs.get_tab(NUM_TABS - i))

    # open menu bar and reopen recently closed tabs
    panel.open()
    panel.reopen_recently_closed_tabs()

    # go through all the tabs and ensure they were the ones that were opened previously
    for i in range(NUM_TABS):
        driver.switch_to.window(driver.window_handles[-1])
        current_page = driver.current_url
        logging.info(f"The current URL is: {current_page}")
        assert current_page in LINK_SET
