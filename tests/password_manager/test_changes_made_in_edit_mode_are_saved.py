import pytest
from selenium.webdriver import Firefox

from modules.page_object_about_pages import AboutLogins

URL_TO_TEST = "https://mozilla.github.io/"
USERNAME = "username"
PASSWORD = "password"
NEW_USERNAME = "Testuser"
ADD_TO_PASSWORD = "123"
NEW_PASSWORD = "password123"


@pytest.fixture()
def test_case():
    return "2241121"


def test_changes_made_in_edit_mode_are_saved(driver: Firefox):
    """
    C2241121 - Verify that changes made in Edit Mode are saved
    """
    # Instantiate object
    about_logins = AboutLogins(driver)

    # Open about:logins and add a new login
    about_logins.open()
    about_logins.click_add_login_button()
    about_logins.create_new_login(
        {
            "origin": URL_TO_TEST,
            "username": USERNAME,
            "password": PASSWORD,
        }
    )
    # Click the "Edit" button
    about_logins.click_on("edit-login")

    # Change username and the password
    about_logins.get_element("about-logins-page-username-field").send_keys(NEW_USERNAME)
    about_logins.get_element("about-logins-page-password-hidden").send_keys(
        ADD_TO_PASSWORD
    )

    # Click the "Save" button
    about_logins.click_on("save-edited-login")

    # Verify the username field is changed
    about_logins.expect_element_attribute_contains(
        "about-logins-page-username-field", "value", NEW_USERNAME
    )

    # Click the "Show Password" button
    about_logins.click_on("show-password-checkbox")

    # Verify the newly entered password is correctly displayed
    about_logins.expect_element_attribute_contains(
        "about-logins-page-password-revealed", "value", NEW_PASSWORD
    )
