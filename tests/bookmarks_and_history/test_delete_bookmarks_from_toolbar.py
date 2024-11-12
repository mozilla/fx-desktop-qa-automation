import pytest
from pynput.keyboard import Controller, Key
from time import sleep
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.browser_object_tabbar import TabBar
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "2084550"


URL_TO_BOOKMARK = "https://www.mozilla.org/"


def test_open_bookmarks_from_toolbar(driver: Firefox):
    """
    C2084550: Verify that the user can open Bookmarks from the Toolbar with a mouse click
    """
    # Instantiate objects
    nav = Navigation(driver)
    panel = PanelUi(driver)
    keyboard = Controller()
    
    page = GenericPage(driver, url=URL_TO_BOOKMARK)
    sleep(5)

    # Bookmark the given website via star button
    driver.get(URL_TO_BOOKMARK)
    nav.add_bookmark_via_star()

    with driver.context(driver.CONTEXT_CHROME):
        # Verify that the bookmark is added
        panel.element_exists("bookmark-by-title", labels=["Internet for people"])

        # Delete the bookmark
        panel.context_click("bookmark-by-title", labels=["Internet for people"])
        sleep(10)
        for _ in range(5):
            keyboard.tap(Key.down)
        keyboard.tap(Key.enter)

        # Verify bookmark is deleted
        panel.element_does_not_exist("bookmark-by-title", labels=["Internet for people"])

