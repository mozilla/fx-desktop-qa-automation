import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutLogins

WEBSITE_ADDRESS = "mozilla.org"
USERNAME = "Â£$Âµâ†’â€œ"
PASSWORD = "Â£$Âµâ†’â€œ"


@pytest.fixture()
def test_case():
    return "2241113"


def test_add_password_non_ascii_chars(driver: Firefox):
    """
    C2241113 Add password - non-ascii characters
    """
    # Instantiate object
    about_logins = AboutLogins(driver)

    # Open about:logins and click on the "Add password" button
    about_logins.open()
    original_logins_amount = len(about_logins.get_elements("login-list-item"))
    about_logins.click_add_login_button()

    # Complete all the fields with valid data and click the "Save" button.
    about_logins.create_new_login(
        {
            "origin": WEBSITE_ADDRESS,
            "username": USERNAME,
            "password": PASSWORD,
        }
    )

    # Check password added in the listbox
    about_logins.wait.until(
        lambda _: len(about_logins.get_elements("login-list-item"))
        > original_logins_amount
    )
    logins = about_logins.get_elements("login-list-item")

    mozilla_login = next(
        login for login in logins if login.get_attribute("title") == WEBSITE_ADDRESS
    )
    assert mozilla_login
