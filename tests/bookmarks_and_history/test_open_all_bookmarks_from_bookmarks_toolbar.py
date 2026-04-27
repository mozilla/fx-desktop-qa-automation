import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "2084564"


BOOKMARK_URLS = [
    "https://www.reddit.com/",
    "https://www.youtube.com/",
    "https://www.mozilla.org/",
]
UNBOOKMARKED_URL = "https://www.wikipedia.org/"
EXPECTED_URL_SITE_NAME = ["reddit", "youtube", "mozilla"]


def test_open_all_bookmarks_from_bookmarks_toolbar(driver: Firefox):
    """
    C2084564: Verify that the user can Open all the bookmarks from the Bookmarks Toolbar
    """
    # Instantiate objects
    nav = Navigation(driver)
    page = GenericPage(driver)

    # Have a few Bookmarks saved on Toolbar
    for url in BOOKMARK_URLS:
        GenericPage(driver, url=url).open()
        nav.add_bookmark_via_star_icon()

    # Load a page that we didn't bookmark, so we can ensure that we're not just picking up on that instance of the page
    GenericPage(driver, url=UNBOOKMARKED_URL).open()

    # Right-click on a blank space from Bookmarks Toolbar menu and choose Open All Bookmarks from the context menu
    nav.open_all_bookmarks_via_context_menu()

    # Check that all the bookmarks from the Bookmarks Toolbar are opened in New Tabs
    for index, url_site_name in enumerate(EXPECTED_URL_SITE_NAME, start=1):
        driver.switch_to.window(driver.window_handles[index])
        page.url_contains(url_site_name)
