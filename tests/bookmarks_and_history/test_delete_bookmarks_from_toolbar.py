import pytest
from pynput.keyboard import Controller, Key
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi


@pytest.fixture()
def test_case():
    return "2084559"


URL_TO_BOOKMARK = "https://www.mozilla.org/"


@pytest.mark.headed
def test_delete_bookmarks_from_toolbar(driver: Firefox):
    """
    C2084559: Verify that the user can delete items from "Bookmarks Toolbar"
    """
    # Instantiate objects
    nav = Navigation(driver)
    panel = PanelUi(driver)
    keyboard = Controller()

    # Bookmark the given website via star button
    driver.get(URL_TO_BOOKMARK)
    nav.add_bookmark_via_star()

    with driver.context(driver.CONTEXT_CHROME):
        # Verify that the bookmark is added
        panel.element_exists("bookmark-by-title", labels=["Internet for people"])

        # Delete the bookmark
        panel.context_click("bookmark-by-title", labels=["Internet for people"])
        for _ in range(5):
            keyboard.tap(Key.down)
        keyboard.tap(Key.enter)

        # Verify bookmark is deleted
        panel.element_not_visible("bookmark-by-title", labels=["Internet for people"])
