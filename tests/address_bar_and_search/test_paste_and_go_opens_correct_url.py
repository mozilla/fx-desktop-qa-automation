from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation

URL = "https://developer.mozilla.org"


@pytest.fixture()
def test_case():
    return "3028883"


def test_paste_and_go_opens_correct_url(driver: Firefox, pyperclip=None):
    """
    C3028883 - "Paste and Go" opens the right URL
    """

    # Instantiate object
    nav = Navigation(driver)

    # Copy the link
    pyperclip.copy(URL)

    # Open a new tab and right click in the Address bar and choose Paste and Go
    nav.get_awesome_bar()
    nav.click_and_hide_menu("context-menu-paste-and-go")
    sleep(5)

    # Check that the page is displayed
