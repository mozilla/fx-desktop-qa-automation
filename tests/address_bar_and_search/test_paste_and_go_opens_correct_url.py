import pytest
from selenium.webdriver import Firefox, Keys

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage

CLIPBOARD_PAGE = "https://bug1320502.bmoattachments.org/attachment.cgi?id=8814655"
URL = "https://developer.mozilla.org"


@pytest.fixture()
def test_case():
    return "3028883"


def test_paste_and_go_opens_correct_url(driver: Firefox):
    """
    C3028883 - "Paste and Go" opens the right URL
    """

    # Instantiate objects
    nav = Navigation(driver)
    page = GenericPage(driver, url=CLIPBOARD_PAGE)

    # Copy the link from the clipboard
    page.open()
    page.click_on("url-to-copy")
    page.perform_key_combo(Keys.COMMAND, "a")
    page.copy()

    # Open a new tab and right click in the Address bar and choose Paste and Go
    nav.open_and_switch_to_new_window("tab")
    nav.get_awesome_bar()
    nav.click_and_hide_menu("context-menu-paste-and-go")

    # Check that the page is displayed
    nav.url_contains(URL)
