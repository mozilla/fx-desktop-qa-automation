import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi


@pytest.fixture()
def test_case():
    return "2084539"


URL_TO_BOOKMARK = "https://www.mozilla.org/"
BOOKMARK_TITLE = "Internet for people"


@pytest.mark.ci
def test_bookmark_website_via_star(driver: Firefox):
    """
    C2084539: Verify that the Websites can be bookmarked via star-shaped button
    """
    # Instantiate object
    nav = Navigation(driver)
    panel = PanelUi(driver)

    # Navigate to test website
    driver.get(URL_TO_BOOKMARK)

    # Bookmark using star button and verify star turned blue
    nav.add_bookmark_via_star_icon()
    nav.verify_star_button_is_blue()

    # Verify bookmark appears in bookmarks menu
    panel.open_bookmarks_panel_from_hamburger_menu()
    panel.verify_bookmark_exists_in_hamburger_menu(BOOKMARK_TITLE)
