import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation
from modules.classes.bookmark import Bookmark
from modules.page_object import GenericPage
from modules.util import BrowserActions

BOOKMARK_URL = "about:robots"
BOOKMARK_URL_2 = "about:cache"
BOOKMARK_NAME = "Cache"
BOOKMARK_TAGS = "a"
BOOKMARK_KEYBOARD = "about"


@pytest.fixture()
def test_case():
    return "2084524"


def test_delete_other_bookmarks(driver: Firefox):
    """
    C2084524 - Verify that a user can Delete a bookmark from 'Other Bookmarks' folder
    """
    nav = Navigation(driver)
    page = GenericPage(driver, url=BOOKMARK_URL)
    ba = BrowserActions(driver)
    context_menu = ContextMenu(driver)

    # Create the first bookmark in Other Bookmarks folder
    page.open()
    nav.bookmark_page_other()

    # Create a new bookmark from Other Bookmark context menu
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("other-bookmarks").click()
        nav.context_click("other-bookmarks-popup")
        context_menu.get_element("context-menu-add-bookmark").click()

        context_menu.hide_popup_by_child_node("context-menu-add-bookmark")
        nav.hide_popup("OtherBookmarksPopup")

    nav.add_bookmark_via_other_bookmark_context_menu(
        Bookmark(BOOKMARK_URL_2, BOOKMARK_NAME, BOOKMARK_TAGS, BOOKMARK_KEYBOARD), ba
    )

    # Delete the first bookmark and verify it's not present anymore
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("other-bookmarks").click()
        nav.context_click("bookmark-about-robots")
        context_menu.click_and_hide_menu("context-menu-delete-page")
        nav.element_not_visible("bookmark-about-robots")
