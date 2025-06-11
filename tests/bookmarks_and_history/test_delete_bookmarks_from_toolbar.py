import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "2084559"


BOOKMARK_URL = "https://www.mozilla.org/"


@pytest.mark.headed
def test_delete_bookmarks_from_toolbar(driver: Firefox):
    """
    C2084559: Verify that the user can delete items from the Bookmarks Toolbar
    """
    # Instantiate objects
    nav = Navigation(driver)
    page = GenericPage(driver, url=BOOKMARK_URL)

    # Bookmark using star button
    page.open()
    nav.add_bookmark_via_star_icon()

    # Verify bookmark was added to toolbar
    nav.verify_bookmark_exists_in_bookmarks_toolbar("Internet for people")

    # Delete the bookmark from toolbar
    nav.delete_bookmark_from_bookmarks_toolbar("Internet for people")

    # Verify bookmark was deleted
    nav.verify_bookmark_does_not_exist_in_bookmarks_toolbar("Internet for people")
