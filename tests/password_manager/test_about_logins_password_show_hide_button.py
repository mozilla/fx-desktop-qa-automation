import pytest
from selenium.webdriver import Firefox

from modules.page_object_about_pages import AboutLogins

TEST_PAGE_URL = "https://mozilla.github.io/"
USERNAME = "username1"
PASSWORD = "password1"


@pytest.fixture()
def test_case():
    return "2241092"


def test_about_logins_password_show_hide_button(driver: Firefox):
    """
    C2241092 - Verify that the Show/Hide Password buttons function correctly
    """

    # Instantiate objects
    about_logins = AboutLogins(driver)

    # Open about:logins and have at least one login is saved
    about_logins.open()
    about_logins.add_login(TEST_PAGE_URL, USERNAME, PASSWORD)

    # Click the "Show" button next to the password field
    about_logins.click_reveal_password_button()

    # The password is shown, the button changes to a "Hide" button
    about_logins.element_visible("show-password-checkbox")

    # Hover over the "Hide" button and check that the mouse cursor changes to a hand pointer
    about_logins.verify_reveal_button_cursor_pointer()

    # Click the "Hide" button
    about_logins.click_reveal_password_button()

    # The password is hidden again, the button changes back to "Show" button
    about_logins.element_visible("password-hidden")
