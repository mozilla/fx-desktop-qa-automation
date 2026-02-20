import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.page_object_generics import GenericPage

BOOKMARK_URL = "https://www.mozilla.org/"
BOOKMARK_NAME = "Mozilla - Internet for people, not profit (US)"


@pytest.fixture()
def test_case():
    return "101679"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.privatebrowsing.resetPBM.enabled", True),
        ("browser.privatebrowsing.felt-privacy-v1", True),
        ("browser.toolbars.bookmarks.visibility", "always"),
    ]


def test_add_bookmark_via_private_browsing_visible_in_regular_browsing(driver: Firefox):
    """
    C101679 - Bookmarks created in Private Browsing are shown in regular sessions as well
    """

    # Instantiate objects
    nav = Navigation(driver)
    panel = PanelUi(driver)
    page = GenericPage(driver, url=BOOKMARK_URL)

    # Open a private window and switch to it
    panel.open_and_switch_to_new_window("private")

    # Access several websites of your choice and bookmark them
    page.open()
    nav.add_bookmark_via_star_icon()

    # Close the private window
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    # The created bookmarks inside the Private Browsing session are successfully displayed in normal browsing
    nav.verify_bookmark_exists_in_bookmarks_toolbar(BOOKMARK_NAME)
