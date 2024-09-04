import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi


@pytest.fixture()
def test_case():
    return "2084489"


URL_TO_BOOKMARK = "https://www.mozilla.org/"


def test_bookmark_via_bookmark_menu(driver: Firefox):
    """
    C2084489: Verify that the user can Bookmark a page from the Bookmarks menu
    """
    # instantiate object
    nav = Navigation(driver)
    panel = PanelUi(driver)

    # Bookmark the given website via bookmarks menu
    driver.get(URL_TO_BOOKMARK)
    panel.open_bookmarks_menu()
    with driver.context(driver.CONTEXT_CHROME):
        panel.get_element("bookmark-current-tab").click()
        nav.get_element("save-bookmark-button").click()

    # Verify that the bookmark is displayed in bookmarks menu
    panel.open_bookmarks_menu()
    panel.element_visible("bookmark-by-title", labels=["Internet for people"])
