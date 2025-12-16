from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_context_menu import ContextMenu
from modules.browser_object_tabbar import TabBar


NUM_TABS = 2

GROUP_1_NAME = "group1"
GROUP_2_NAME = "group2"

GROUP_1_URLS = [
    "https://example.com",
    "https://www.mozilla.org",
]

GROUP_2_URLS = [
    "https://www.wikipedia.org",
    "https://www.python.org",
]


@pytest.fixture()
def test_case():
    return "2804875"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.tabs.groups.enabled", True),
        ("browser.tabs.groups.dragOverThresholdPercent", 20),
    ]


def test_restore_closed_tabs_previous_groups(driver: Firefox):
    """
    C2804875 - Verify that closed tabs can be restored to their previous Groups
    """

    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)

    tabs.create_tab_group_website(
        group_name="Group 1",
        tab_context_menu=context_menu,
        urls=GROUP_1_URLS,
    )

    sleep(5)

    # ---- Create second group ----
    tabs.create_tab_group_website(
        group_name="Group 2",
        tab_context_menu=context_menu,
        urls=GROUP_2_URLS,
    )

    sleep(500)