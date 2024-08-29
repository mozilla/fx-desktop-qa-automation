import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi


@pytest.fixture()
def test_case():
    return "2084539"


URL_TO_BOOKMARK = "https://www.mozilla.org/"


def test_bookmark_website_via_star(driver: Firefox):
    """
    C2084539: Verify that the Websites can be bookmarked via star-shaped button
    """
    # instantiate object
    nav = Navigation(driver)
    panel = PanelUi(driver)

    # Bookmark the given website and check the bookmark star turned blue
    driver.get(URL_TO_BOOKMARK)
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("star-button").click()
        nav.get_element("save-bookmark-button").click()
        nav.element_visible("blue-star-button")

    # Verify that the bookmark is displayed in bookmarks menu
    panel.open_bookmarks_menu()
    panel.element_visible("bookmark-by-title", labels=["Internet for people"])
