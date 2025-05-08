import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutLogins


@pytest.fixture()
def test_case():
    return "2241113"


WEBSITE_ADDRESS = "mozilla.org"


def test_add_password_non_ascii_chars(driver: Firefox):
    """
    C2241113 Add password - non-ascii characters
    """
    # Instantiate object
    about_logins = AboutLogins(driver)

    # Open about:logins and click on the "Add password" button
    about_logins.open()
    about_logins.click_add_login_button()

    # Complete all the fields with valid data and click the "Save" button.
    about_logins.create_new_login(
        {
            "origin": "mozilla.org",
            "username": "Â£$Âµâ†’â€œ",
            "password": "Â£$Âµâ†’â€œ",
        }
    )

    # Check password added in the listbox
    about_logins.get_element("login-list-item")
    logins = about_logins.get_elements("login-list-item")
    mozilla_login = next(
        login for login in logins if login.get_attribute("title") == WEBSITE_ADDRESS
    )
    assert mozilla_login
