import pytest
from selenium.webdriver import Firefox

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
EXPECTED_URL_PARTS = ["reddit", "youtube", "mozilla"]


def test_open_all_bookmarks_from_bookmarks_toolbar(driver: Firefox):
    """
    C2084564 - Verify that the user can Open all the bookmarks from the Bookmarks Toolbar
    """
    # Instantiate objects
    nav = Navigation(driver)
    panel = PanelUi(driver)
    page = GenericPage(driver)

    # Have a few Bookmarks saved on the Toolbar
    urls_to_bookmark = [URL1_TO_BOOKMARK, URL2_TO_BOOKMARK, URL3_TO_BOOKMARK]
    for url in urls_to_bookmark:
        GenericPage(driver, url=url).open()
        nav.add_bookmark_via_star_icon()

    # Load a page that we didn't bookmark
    GenericPage(driver, url=URL_NOT_BOOKMARKED).open()

    # Right-click on bookmarks toolbar and open all bookmarks
    panel.open_all_bookmarks_via_context_menu()

    # Check that all the bookmarks are opened in New Tabs
    for index, url_part in enumerate(EXPECTED_URL_PARTS, start=1):
        driver.switch_to.window(driver.window_handles[index])
        page.url_contains(url_part)
