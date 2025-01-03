import logging
import sys
from os import environ

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar


@pytest.fixture()
def test_case():
    return "134647"


WIN_GHA = environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("win")


@pytest.mark.skipif(WIN_GHA, reason="Test unstable in Windows Github Actions")
def test_navigation_multiple_tabs(driver: Firefox):
    """C134647 - Verify that Multiple Tabs can be closed via the context menu"""
    # open 20 tabs
    tabs = TabBar(driver)
    num_tabs = 20

    for _ in range(num_tabs):
        tabs.new_tab_by_button()

    # after opening 20 tabs, should be at the right most tab
    with driver.context(driver.CONTEXT_CHROME):
        # get the last tab, verify that upon double clicking the left scroll position decreased
        last_tab = tabs.get_tab(21)
        original_location_pre_left = last_tab.location["x"]
        tabs.double_click("tab-scrollbox-left-button", labels=[])
        new_location_post_left = last_tab.location["x"]

        logging.info(f"The original position: {original_location_pre_left}")
        logging.info(f"The new position: {new_location_post_left}")
        assert new_location_post_left < original_location_pre_left

        # get the first tab, verify that upon clicking the right scroll position increased
        first_tab = tabs.get_tab(1)
        original_location_pre_right = first_tab.location["x"]
        tabs.double_click("tab-scrollbox-right-button", labels=[])
        new_location_post_right = first_tab.location["x"]

        logging.info(f"The original position: {original_location_pre_right}")
        logging.info(f"The new position: {new_location_post_right}")
        assert new_location_post_right > original_location_pre_right
