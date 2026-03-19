import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi
from modules.page_object import GenericPage

BOOKMARK_URL = "https://www.mozilla.org/"
BOOKMARK_NAME = "Mozilla - Internet for people, not profit (US)"


@pytest.fixture()
def test_case():
    return "101743"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.privatebrowsing.resetPBM.enabled", True),
        ("browser.privatebrowsing.felt-privacy-v1", True),
        ("browser.toolbars.bookmarks.visibility", "always"),
    ]


def test_bookmarks_removed_via_private_browsing(
    driver: Firefox, panel_ui: PanelUi, nav: Navigation
):
    """
    C101743: Bookmarks can be successfully removed via Private Browsing
    """

    # Instantiate objects
    page = GenericPage(driver, url=BOOKMARK_URL)

    # Open a private window and switch to it
    panel_ui.open_and_switch_to_new_window("private")

    # Access any websites bookmark it
    page.open()
    nav.add_bookmark_via_star_icon()

    # The created bookmarks inside the Private Browsing session are successfully displayed
    nav.verify_bookmark_exists_in_bookmarks_toolbar(BOOKMARK_NAME)

    # Delete an existing bookmark
    nav.delete_panel_menu_item_by_title("Internet for people")

    # Close the private window
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    # The Bookmark that was previously removed via the Private Browsing is no longer displayed
    nav.verify_bookmark_does_not_exist_in_bookmarks_toolbar("Internet for people")
