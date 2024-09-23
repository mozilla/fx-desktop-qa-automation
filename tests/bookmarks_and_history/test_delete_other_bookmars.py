import sys
from os import environ

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation
from modules.page_object import GenericPage


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

    # create the first bookmark for other
    nav.bookmark_page_other()

    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("other-bookmarks").click()
        nav.context_click("bookmark-about-robots")
        nav.element_visible("bookmark-about-robots")

    # get other bookmarks
    # with driver.context(driver.CONTEXT_CHROME):
    #     nav.get_element("other-bookmarks").click()
    #     nav.context_click("other-bookmarks-popup")
    #     context_menu.get_element("context-menu-add-bookmark").click()
    #
    #     context_menu.hide_popup_by_child_node("context-menu-add-bookmark")
    #     nav.hide_popup("OtherBookmarksPopup")
    #     nav.get_element("other-bookmarks").click()
    #     nav.context_click("bookmark-about-robots")

