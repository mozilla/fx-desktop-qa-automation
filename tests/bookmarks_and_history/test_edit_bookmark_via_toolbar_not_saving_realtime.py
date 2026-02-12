import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.page_object_generics import GenericPage


BOOKMARK_URL = "https://www.mozilla.org/"


@pytest.fixture()
def test_case():
    return "2090451"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.toolbars.bookmarks.visibility", "always")]


def test_edit_bookmark_via_toolbar_not_saving_realtime(driver: Firefox):
    """
    C2090396 - Verify that Editing a Bookmark from the Bookmarks Toolbar will not save it in real time
    """

    # Instantiate objects
    nav = Navigation(driver)
    panel = PanelUi(driver)
    page = GenericPage(driver, url=BOOKMARK_URL)

    # Have at Least 1 Bookmark saved on the Bookmarks toolbar
    page.open()
    nav.add_bookmark_via_star_icon()

    # Right Click any Bookmark from the Bookmarks Toolbar and select the Edit Bookmark option

    # Edit the Name into something with more characters

    # The modified name is not updated in real time.
    # THe Bookmarks toolbar still shows the old Bookmark name

    # Click the Save button.

    # The new edited name is now displayed on the Bookmarks Toolbar
