import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "2084550"


BOOKMARK_URL = "https://www.mozilla.org/"
BOOKMARK_TITLE = "Internet for people"


def test_open_bookmarks_from_toolbar(driver: Firefox):
    """
    C2084550: Verify that the user can open Bookmarks from the Toolbar with a mouse click
    """
    # Instantiate object
    nav = Navigation(driver)
    tab = TabBar(driver)
    page = GenericPage(driver, url=BOOKMARK_URL)

    # Bookmark the given website via star button
    page.open()
    nav.add_bookmark_via_star_icon()

    # Open new tab and click on the bookmark from the Bookmarks Toolbar
    tab.new_tab_by_button()
    nav.open_bookmark_from_toolbar(BOOKMARK_TITLE)

    # Verify that the page is loaded
    page.title_contains("Internet for people")
