import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.classes.bookmark import Bookmark
from modules.page_object import GenericPage
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "2084518"


BOOKMARK = Bookmark(url="about:robots", name="Robots 2", tags="a", keyword="about")


def test_add_new_other_bookmark(driver: Firefox):
    """
    C2084518 - Verify another bookmark (with name, url, tag, keyword) can be added from other bookmarks toolbar
    context menu
    """
    nav = Navigation(driver)
    ba = BrowserActions(driver)
    page = GenericPage(driver, url=BOOKMARK.url)

    # Create the first bookmark in Other Bookmarks folder
    page.open()
    nav.bookmark_page_in_other_bookmarks()

    # Create a new bookmark from Toolbar Other Bookmark context menu
    nav.open_add_bookmark_via_toolbar_other_bookmarks_context_menu()
    nav.add_bookmark_via_toolbar_other_bookmark_context_menu(BOOKMARK, ba)

    # Verify the bookmark is present in Other Bookmarks folder
    nav.verify_bookmark_exists_in_toolbar_other_bookmarks_folder(BOOKMARK.name)
