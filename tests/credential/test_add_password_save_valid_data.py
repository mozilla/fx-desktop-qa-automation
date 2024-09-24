from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.page_object import AboutLogins


@pytest.fixture()
def test_case():
    return "2241112"


def test_add_password_save_valid_data(driver: Firefox):
    """
    C2241112 Verify that a password can be added and saved
    """
    # instantiate object
    about_logins = AboutLogins(driver).open()

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

    # Check the "Sort by:" dropdown from the top part of the Login list becomes active
    AboutLogins(driver).open()
    about_logins.get_element("login-sort").click()

    # The <number> password from the right side of the "Sort by:" dropdown is updated
