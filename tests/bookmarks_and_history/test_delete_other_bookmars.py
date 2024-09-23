import sys
from os import environ

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation
from modules.classes.bookmark import Bookmark
from modules.page_object import GenericPage
from modules.util import BrowserActions


BOOKMARK_URL = "about:robots"
BOOKMARK_URL_2 = "about:cache"


WIN_GHA = environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("win")


@pytest.mark.skipif(WIN_GHA, reason="Test unstable in Windows Github Actions")
def test_delete_other_bookmarks(driver: Firefox):
    """
        C2084524: Verify that a user can Delete a bookmark from 'Other Bookmarks' folder
    """
    nav = Navigation(driver)
    GenericPage(driver, url=BOOKMARK_URL).open()
    ba = BrowserActions(driver)
    context_menu = ContextMenu(driver)

    # create the first bookmark for other
    nav.bookmark_page_other()

    # get other bookmarks
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("other-bookmarks").click()
        nav.context_click("other-bookmarks-popup")
        context_menu.get_element("context-menu-add-bookmark").click()

        context_menu.hide_popup_by_child_node("context-menu-add-bookmark")
        nav.hide_popup("OtherBookmarksPopup")

    # add second bookmark
    nav.add_bookmark_advanced(Bookmark(url=BOOKMARK_URL_2, name="Cache"), ba)

    # delete first bookmark and verify it's not present anymore
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("other-bookmarks").click()
        nav.context_click("bookmark-about-robots")
        context_menu.click_and_hide_menu("context-menu-delete-page")
        nav.element_not_visible("bookmark-about-robots")

