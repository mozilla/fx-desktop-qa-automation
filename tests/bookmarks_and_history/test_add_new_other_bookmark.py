import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation
from modules.classes.bookmark import Bookmark
from modules.page_object import GenericPage
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "2084518"


BOOKMARK_URL = "about:robots"
BOOKMARK_NAME = "Robots 2"
BOOKMARK_TAGS = "a"
BOOKMARK_KEYBOARD = "about"


def test_add_new_other_bookmark(driver: Firefox):
    """
    C2084518 - Verify another bookmark (with name, url, tag, keyboard) can be added from other bookmarks toolbar
    context menu
    """
    nav = Navigation(driver)
    ba = BrowserActions(driver)
    page = GenericPage(driver, url=BOOKMARK_URL)
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
            Bookmark(BOOKMARK_URL, BOOKMARK_NAME, BOOKMARK_TAGS, BOOKMARK_KEYBOARD), ba
        )

    # Verify the presence of the second added bookmarked page
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("other-bookmarks").click()
        nav.element_visible("bookmark-robots")
