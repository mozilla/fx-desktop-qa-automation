import logging

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar


@pytest.fixture()
def test_case():
    return "134723"


def test_change_position_of_pinned_tabs(driver: Firefox):
    tabs = TabBar(driver)
    tab_context_menu = ContextMenu(driver)

    tab_titles = []
    url_list = ["about:logo", "about:robots", "https://mozilla.org"]

    driver.get(url_list[0])
    tab_titles.append(driver.title)

    # Open 3 tabs
    for i in range(1, len(url_list)):
        tabs.new_tab_by_button()
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(url_list[i])
        tab_titles.append(driver.title)

    # Specific tabs we want to work with
    robot_title = tab_titles[1]
    mozilla_title = tab_titles[2]

    # Pin the 'Robots' tab by its title
    driver.switch_to.window(driver.window_handles[0])
    robot_tab = tabs.get_tab(robot_title)
    assert robot_tab is not None, "Robot tab should exist"
    tabs.context_click(robot_tab)
    tab_context_menu.click_and_hide_menu("context-menu-pin-tab")
    pinned_tab_one = tabs.get_tab(robot_title)
    assert tabs.is_pinned(pinned_tab_one)

    # Pin the 'Mozilla' tab by its title
    mozilla_tab = tabs.get_tab(mozilla_title)
    assert mozilla_tab is not None, "Mozilla tab should exist"
    tabs.context_click(mozilla_tab)
    tab_context_menu.click_and_hide_menu("context-menu-pin-tab")
    pinned_tab_two = tabs.get_tab(mozilla_title)
    assert tabs.is_pinned(pinned_tab_two)

    # Move second pinned tab to the left
    tabs.context_click(pinned_tab_two)
    tab_context_menu.click_and_hide_menu("context-menu-move-tab-to-start")

    # Get the titles for each of the rearranged pinned tabs
    driver.switch_to.window(driver.window_handles[0])
    new_pinned_tab_one_title = driver.title
    logging.info("Tab title: %s", new_pinned_tab_one_title)

    driver.switch_to.window(driver.window_handles[1])
    new_pinned_tab_two_title = driver.title
    logging.info("Tab title: %s", new_pinned_tab_two_title)

    assert "Mozilla" in new_pinned_tab_one_title, (
        "Mozilla should now be the first pinned tab"
    )
    assert "Gort!" in new_pinned_tab_two_title, (
        "Robot should now be the second pinned tab"
    )
