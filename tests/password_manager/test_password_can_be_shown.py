import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutLogins
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "2264688"

def test_password_can_be_shown(driver:Firefox):
    """
    C2264688: Verify that the Show Password button prompts for the Primary Password before revealing the saved login
    """
    # instantiate object
    about_logins = AboutLogins(driver).open()
    about_prefs = AboutPrefs(driver).open()

    # Click on the "Add password" button
    about_logins.click_add_login_button()

    # Complete all the fields with valid data and click the "Save" button.
    about_logins.create_new_login(
        {
            "origin": "mozilla.org",
            "username": "username",
            "password": "password",
        }
    )

    about_prefs.set_primary_password("1")  # Setting "1" as the primary password

    show_password_button = about_logins.get_element("show-password-checkbox")
    show_password_button.click()

    about_logins.input_primary_password_for_showing("1")  # Input the primary password "1" again
    #Assert that the password is now visible (input type should be 'text')

    password_field = about_logins.get_element("about-logins-page-password-field")
    password_type = password_field.get_attribute("type")

    assert password_type == "text", "Password should be visible after entering the primary password"
