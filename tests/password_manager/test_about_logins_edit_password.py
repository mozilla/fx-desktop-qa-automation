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
    about_logins.click_shadow_element(first_login)
    
    shadow_host = about_logins.get_element("login-items")
    shadow_content = about_logins.utils.get_shadow_content(shadow_host)

    edit_button = shadow_content[0].find_element("css selector", "edit-button")
    edit_button.click()


    new_username = faker.user_name()
    new_password = faker.password(length=15)
    ba.clear_and_fill(about_logins.get_element("about-logins-page-username-field"), new_username, press_enter=False)
    password_field = about_logins.get_element("about-logins-page-password-field")
    driver.execute_script("arguments[0].value = arguments[1];", password_field, new_password)
    about_logins.wait.until(lambda _: about_logins.get_element("about-logins-page-password-field").get_attribute("value") == new_password)

    save_button = shadow_content[0].find_element("css selector", ".save-changes-button")
    save_button.click()

