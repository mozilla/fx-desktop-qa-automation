import pytest
from selenium.webdriver import Firefox

from modules.browser_object_context_menu import ContextMenu
from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "2084564"


URL1_TO_BOOKMARK = "https://www.reddit.com/"
URL2_TO_BOOKMARK = "https://www.youtube.com/"
URL3_TO_BOOKMARK = "https://www.mozilla.org/"
URL_NOT_BOOKMARKED = "https://www.wikipedia.org/"


def test_open_all_bookmarks_from_bookmarks_toolbar(driver: Firefox):
    """
    C2084564: Verify that the user can Open all the bookmarks from the Bookmarks Toolbar
    """
    # instantiate object
    nav = Navigation(driver)
    panel = PanelUi(driver)
    context_menu = ContextMenu(driver)
    page = GenericPage(driver)

    # Have a few Bookmarks saved on the Toolbar
    urls_to_bookmark = [URL1_TO_BOOKMARK, URL2_TO_BOOKMARK, URL3_TO_BOOKMARK]
    for url in urls_to_bookmark:
        GenericPage(driver, url=url).open()
        nav.add_bookmark_via_star()

    # Load a page that we didn't bookmark, so we can ensure that we're not just picking up on that instance of the page
    GenericPage(driver, url=URL_NOT_BOOKMARKED).open()

    # Toggle bookmarks toolbar
    nav.toggle_bookmarks_toolbar_with_key_combo()

    # Right-click on a blank space from Bookmarks Toolbar menu and choose open all bookmarks
    panel.context_click("bookmarks-toolbar")
    context_menu.click_and_hide_menu("context-menu-toolbar-open-all-bookmarks")

    # Check that all the bookmarks from the Bookmarks Toolbar are opened in New Tabs
    expected_urls = ["reddit", "youtube", "mozilla"]
    for index, url_part in enumerate(expected_urls, start=1):
        driver.switch_to.window(driver.window_handles[index])
        page.url_contains(url_part)
