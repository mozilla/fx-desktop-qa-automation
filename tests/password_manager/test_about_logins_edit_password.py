import pytest

from modules.page_object import AboutLogins
from modules.util import BrowserActions
from faker import Faker


@pytest.fixture()
def test_case():
    return "2241083"


def test_about_logins_edit_password(driver_and_saved_logins, faker: Faker):
    """
    C2241083 - Verifies editing the password of an existing login entry in the about:logins page.
    """
    (driver, usernames, logins) = driver_and_saved_logins
    ba = BrowserActions(driver)
    about_logins = AboutLogins(driver).open()
    ba.clear_and_fill(about_logins.get_element("login-filter-input"), usernames[-1])
    login_results = about_logins.get_elements("login-list-item")
    first_login = login_results[0]
    driver.execute_script(
        """
            const firstLogin = arguments[0]
            firstLogin.click();
        """,
    first_login)
    driver.execute_script(
        """
            const shadowHost = arguments[0];
            const shadowRoot = shadowHost.shadowRoot;
            const editButton = shadowRoot.querySelector('edit-button');
            editButton.click();
        """,
        about_logins.get_element("login-items")
    )

    new_username = faker.user_name()
    new_password = faker.password(length=15)
    ba.clear_and_fill(about_logins.get_element("about-logins-page-username-field"), new_username, press_enter=False)
    password_field = about_logins.get_element("about-logins-page-password-field")
    driver.execute_script("arguments[0].value = arguments[1];", password_field, new_password)
    displayed_password = about_logins.get_element("about-logins-page-password-field").get_attribute("value")

    shadow_host = about_logins.get_element("login-items")

    driver.execute_script("""
        const shadowRoot = arguments[0].shadowRoot;
        const saveChangesButton = shadowRoot.querySelector('.save-changes-button');
        saveChangesButton.click();
    """, shadow_host)
    assert displayed_password == new_password

