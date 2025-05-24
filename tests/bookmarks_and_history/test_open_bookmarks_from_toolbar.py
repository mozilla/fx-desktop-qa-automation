import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.browser_object_tabbar import TabBar
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "2084550"


URL_TO_BOOKMARK = "https://www.mozilla.org/"
BOOKMARK_TITLE = "Internet for people"


def test_open_bookmarks_from_toolbar(driver: Firefox):
    """
    C2084550 - Verify that the user can open Bookmarks from the Toolbar
    """
    # Instantiate objects
    nav = Navigation(driver)
    panel = PanelUi(driver)
    newtab = TabBar(driver)
    page = GenericPage(driver, url=URL_TO_BOOKMARK)

    # Bookmark the given website via star button
    page.open()
    nav.add_bookmark_via_star_icon()

    # Open new tab and click on the bookmark from the Bookmarks Toolbar
    newtab.new_tab_by_button()
    panel.click_on("bookmark-by-title", labels=[BOOKMARK_TITLE])

    # Verify that the page is loaded
    page.title_contains(BOOKMARK_TITLE)
