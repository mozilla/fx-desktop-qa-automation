from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_about_pages import AboutLogins

TEST_PAGE_URL = "https://mozilla.github.io/"
USERNAME = "username1"
PASSWORD = "password1"


@pytest.fixture()
def test_case():
    return "2241090"


def test_about_logins_username_copy_button(driver: Firefox):
    """
    C2241090 - Verify that Username "Copy" button functions correctly
    """

    # Instantiate objects
    about_logins = AboutLogins(driver)
    nav = Navigation(driver)

    # Open about:logins and have at least one login is saved
    about_logins.open()
    about_logins.add_login(TEST_PAGE_URL, USERNAME, PASSWORD)

    # Click on the "Copy" button next to the username
    about_logins.click_copy_username_button()

    # Open a text editor (Notepad), and paste the copied text (Ctrl + V) or by right-clicking and selecting "Paste"
    nav.clear_awesome_bar()
    nav.paste_in_awesome_bar()

    # The username is correctly pasted
    nav.verify_plain_text_in_input_awesome_bar(USERNAME)
