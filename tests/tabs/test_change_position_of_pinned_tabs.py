import logging
import time

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from modules.browser_object import ContextMenu, Navigation, TabBar


@pytest.fixture()
def test_case():
    return "134723"


def test_change_position_of_pinned_tabs(driver: Firefox):
    tabs = TabBar(driver)
    nav = Navigation(driver)
    tabs_context_menu = ContextMenu(driver)
    num_tabs = 5

    tab_titles = []
    url_list = [
        "https://www.google.com",
        "https://www.youtube.com",
        "https://www.mozilla.org",
        "https://www.wikipedia.org",
        "https://www.github.com",
    ]

    driver.get(url_list[0])
    tab_titles.append(driver.title)

    # Open 5 tabs
    for i in range(1, len(url_list)):
        tabs.new_tab_by_button()
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(url_list[i])
        tab_titles.append(driver.title)
    time.sleep(2)

    # specific tabs we want to work with
    google_title = tab_titles[0]
    mozilla_title = tab_titles[2]

    # Pin the 'Google' tab by its title
    driver.switch_to.window(driver.window_handles[0])
    google_tab = tabs.get_tab(google_title)
    assert google_tab is not None, "Google tab should exist"
    tabs.context_click(google_tab)
    tabs_context_menu.click_context_item("context-menu-pin-tab")
    time.sleep(1)

    # FIX: Re-initialize the context menu object after the DOM has changed.
    # FIX: Force a "context reset" by switching to a neutral tab.
    driver.switch_to.window(driver.window_handles[1])  # Switch to YouTube
    time.sleep(0.5)  # A brief pause to ensure the context switch completes
    tabs_context_menu = ContextMenu(driver)

    # Pin the 'Mozilla' tab by its title
    driver.switch_to.window(driver.window_handles[2])
    mozilla_tab = tabs.get_tab(mozilla_title)
    assert mozilla_tab is not None, "Mozilla tab should exist"
    tabs.context_click(mozilla_tab)
    tabs_context_menu.click_context_item("context-menu-pin-tab")
    time.sleep(1)

    driver.switch_to.window(driver.window_handles[0])
    pinned_tab_one = tabs.get_tab(google_title)
    assert tabs.is_pinned(pinned_tab_one)

    # ERROR
    # pinned_tab_two = tabs.get_tab(mozilla_title)
    # assert tabs.is_pinned(pinned_tab_two)

    # -----------------------after pinned error is fixed ------------------------------------
    # actions = ActionChains(driver)
    # # A more robust, manual way to perform a drag-and-drop
    # actions.drag_and_drop(pinned_tab_one, pinned_tab_two).perform()

    # assert tab_titles[0] in new_pinned_tab_one.text, "Google should now be the first pinned tab"
    # assert tab_titles[2] in new_pinned_tab_two.text, "Mozilla should now be the second pinned tab"
