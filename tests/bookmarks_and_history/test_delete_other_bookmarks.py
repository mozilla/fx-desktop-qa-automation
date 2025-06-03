import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.classes.bookmark import Bookmark
from modules.page_object import GenericPage
from modules.util import BrowserActions

CACHE_PAGE_URL = "about:cache"
ROBOTS_BOOKMARK = Bookmark(
    url="about:robots", name="About Robots", tags="a", keyword="about"
)


@pytest.fixture()
def test_case():
    return "2084524"


def test_delete_other_bookmarks(driver: Firefox):
    """
    C2084524 - Verify that a user can Delete a bookmark from 'Other Bookmarks' folder
    """
    nav = Navigation(driver)
    page = GenericPage(driver, url=CACHE_PAGE_URL)
    ba = BrowserActions(driver)

    # Create the first bookmark in Other Bookmarks folder
    page.open()
    nav.bookmark_page_in_other_bookmarks()

    # Create a new bookmark from Toolbar Other Bookmark context menu
    nav.open_add_bookmark_via_toolbar_other_bookmarks_context_menu()
    nav.add_bookmark_via_toolbar_other_bookmark_context_menu(ROBOTS_BOOKMARK, ba)

    # Delete the second bookmark (About Robots) and verify it's gone
    nav.delete_bookmark_from_other_bookmarks_via_context_menu(ROBOTS_BOOKMARK.name)
    nav.verify_bookmark_does_not_exist_in_toolbar_other_bookmarks_folder(
        ROBOTS_BOOKMARK.name
    )
