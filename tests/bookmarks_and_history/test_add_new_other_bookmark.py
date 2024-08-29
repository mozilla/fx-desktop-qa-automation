import sys
from os import environ

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


WIN_GHA = environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("win")


@pytest.mark.skipif(WIN_GHA, reason="Test unstable in Windows Github Actions")
def test_add_new_other_bookmark(driver: Firefox):
    """
    C2084518: verify user can add another bookmark from other bookmarks
    """
    nav = Navigation(driver)
    ba = BrowserActions(driver)
    GenericPage(driver, url=BOOKMARK_URL).open()
    context_menu = ContextMenu(driver)

    # create a bookmark for other
    nav.bookmark_page_other()

    # get other bookmarks
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("other-bookmarks").click()
        nav.context_click("other-bookmarks-popup")
        context_menu.get_element("context-menu-add-bookmark").click()

        context_menu.hide_popup_by_child_node("context-menu-add-bookmark")
        nav.hide_popup("OtherBookmarksPopup")

    nav.add_bookmark_advanced(Bookmark(url="about:robots", name="Robots 2"), ba)

    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("other-bookmarks").click()
        nav.element_visible("bookmark-robots")
