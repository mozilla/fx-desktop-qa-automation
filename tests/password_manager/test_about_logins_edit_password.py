import pytest

from modules.page_object import AboutLogins
from modules.util import BrowserActions
from faker import Faker


@pytest.fixture()
def test_case():
    return "2241083"

@pytest.fixture()
def temp_selectors():
    return {
        "edit-button": {
            "selectorData": "edit-button",
            "strategy": "tag",
            "groups": [],
        },
        "show-password-button": {
            "selectorData": ".detail-row .reveal-password-wrapper input.reveal-password-checkbox",
            "strategy": "css",
            "shadowParent": "login-item",
            "groups": []
        },
        "not-allowed": {"selectorData": "error", "groups": []},
    }


def test_about_logins_edit_password(driver_and_saved_logins, faker: Faker):
    """
    C2241083 - Verifies editing the password of an existing login entry in the about:logins page.
    """
    (driver, usernames, logins) = driver_and_saved_logins
    ba = BrowserActions(driver)
    about_logins = AboutLogins(driver).open()

    # Step 1: fliter saved logins by username (expect 1 result)
    ba.clear_and_fill(about_logins.get_element("login-filter-input"), usernames[-1])

    # Step 2: Click the result
    login_results = about_logins.get_elements("login-list-item")
    first_login_result = login_results[0]
    first_login_result.click()

    # Step 3: Click the 'Edit' button
    about_logins.get_element("edit-button").click()

    new_username = faker.user_name()
    new_password = faker.password(length=15)

    # Fill in the new username and password
    ba.clear_and_fill(about_logins.get_element("about-logins-page-username-field"), new_username, press_enter=False)
    ba.clear_and_fill(about_logins.get_element("about-logins-page-password-field"), new_password, press_enter=False)

    # Step 5: Save the changes
    about_logins.get_element("save-changes-button").click()

    # Step 6: Show the password and confirm it's updated
    about_logins.get_element("show-password-button").click()
    displayed_password = about_logins.get_element("about-logins-page-password-field").get_attribute("value")

    # Step 7: Assert that the displayed password matches the new one
    assert displayed_password == new_password

