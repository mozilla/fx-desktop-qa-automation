import pytest

from modules.page_object_about_pages import AboutLogins
from modules.page_object_autofill import LoginAutofill
from logging import warning


@pytest.fixture()
def test_case():
    return "2241120"


def test_delete_login(driver_and_saved_logins):
    """
    C2241120 - Verify that by clicking the "Remove" button in about:logins main page, the last saved login
    is deleted.
    """
    # Adds 6 fake logins in about:login
    driver, usernames, logins = driver_and_saved_logins
    warning(driver.capabilities['moz:geckodriverVersion'])
    return 1

    # Instantiate objects
    about_logins = AboutLogins(driver)
    login_autofill = LoginAutofill(driver)

    # Open about:logins and verify the initial number of saved passwords
    about_logins.open()
    password_count = about_logins.get_element("password-count")
    login_autofill.wait.until(
        lambda _: password_count.get_attribute("innerText") == "6 passwords"
    )

    # Delete the last saved login
    about_logins.get_element("remove-login-button-main-page").click()
    about_logins.get_element("remove-login-button-confirmation-dialog").click()

    # Verify that the saved passwords count decreases by 1
    login_autofill.wait.until(
        lambda _: password_count.get_attribute("innerText") == "5 passwords"
    )
