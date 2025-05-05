import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.page_object import AboutLogins


@pytest.fixture()
def test_case():
    return "2241112"


def test_add_password_save_valid_data(driver: Firefox):
    """
    C2241112 Verify that a password can be added and saved
    """
    # instantiate object
    about_logins = AboutLogins(driver)

    # Open about:logins and click on the "Add password" button
    about_logins.open()
    about_logins.click_add_login_button()

    # Complete all the fields with valid data and click the "Save" button.
    about_logins.create_new_login(
        {
            "origin": "mozilla.org",
            "username": "username",
            "password": "password",
        }
    )

    # Check password added in the listbox
    about_logins.get_element("login-list-item")
    logins = about_logins.get_elements("login-list-item")
    mozilla_login = next(
        login for login in logins if login.get_attribute("title") == "mozilla.org"
    )
    assert mozilla_login

    # Check the "Sort by:" dropdown from the top part of the Login list becomes active
    login_sort = about_logins.get_element("login-sort")
    about_logins.expect(EC.element_to_be_clickable(login_sort))

    # The <number> password from the right side of the "Sort by:" dropdown is updated
    pass_count = about_logins.get_element("password-count")
    pass_count_text = pass_count.text
    assert "1 password" in pass_count_text
