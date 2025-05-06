import pytest
from selenium.webdriver import Firefox

from modules.page_object_about_pages import AboutLogins


@pytest.fixture()
def test_case():
    return "2241121"


def test_changes_made_in_edit_mode_are_saved(driver: Firefox):
    """
    C2241121 - Verify that changes made in Edit Mode are saved
    """
    # instantiate object
    about_logins = AboutLogins(driver)

    # Open about:logins and add a new login
    about_logins.open()
    about_logins.click_add_login_button()
    about_logins.create_new_login(
        {
            "origin": "https://mozilla.github.io/",
            "username": "username",
            "password": "password",
        }
    )
    # Click the "Edit" button
    about_logins.click_on("edit-login")

    # Change username and the password
    about_logins.get_element("about-logins-page-username-field").send_keys("Testuser")
    about_logins.get_element("about-logins-page-password-hidden").send_keys("123")

    # Click the "Save" button
    about_logins.click_on("save-edited-login")

    # Verify the username field is changed
    about_logins.expect_element_attribute_contains(
        "about-logins-page-username-field", "value", "Testuser"
    )

    # Click the "Show Password" button
    about_logins.click_on("show-password-checkbox")

    # Verify the newly entered password is correctly displayed
    about_logins.expect_element_attribute_contains(
        "about-logins-page-password-revealed", "value", "password123"
    )
