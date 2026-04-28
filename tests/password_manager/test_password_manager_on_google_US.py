import time

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object import AboutLogins, GenericPage

GOOGLE_LOGIN_URL = "https://accounts.google.com/signin/v2/identifier?hl=ro&passive=true&continue=https%3A%2F%2Fwww.google.com%2F&flowName=GlifWebSignIn&flowEntry=ServiceLogin."
GOOGLE_ORIGIN = "https://accounts.google.com"

USERNAME = "username1@gmail.com"
PASSWORD = "password1"
USERNAME2 = "username2@gmail.com"
PASSWORD2 = "password2"
USERNAME3 = "username3@gmail.com"
PASSWORD3 = "password3"

DENIED_USERNAME = "not_saved@gmail.com"
DENIED_PASSWORD = "not_saved_password"


@pytest.fixture()
def test_case():
    return "2245444"


@pytest.fixture()
def add_to_prefs_list():
    return [("signon.rememberSignons", True), ("signon.autofillForms", True)]


@pytest.fixture()
def temp_selectors():
    return {
        "google-email-field": {
            "selectorData": "identifierId",
            "strategy": "id",
            "groups": ["doNotCache"],
        }
    }


@pytest.mark.headed
def test_google_login_saved_credentials_dropdown(driver: Firefox, temp_selectors):
    """
    Verify saved Google login credentials are available from the password manager
    autocomplete dropdown, while denied credentials are not saved.
    """
    about_logins = AboutLogins(driver)
    autofill_popup = AutofillPopup(driver)

    # 1. Access the Google login page
    google_login_page = GenericPage(driver, url=GOOGLE_LOGIN_URL).open()
    google_login_page.elements |= temp_selectors

    # 2. Input one set of credentials and save them
    about_logins.open()
    about_logins.add_login(GOOGLE_ORIGIN, USERNAME, PASSWORD)

    # 3. Refresh the login page and verify autofill works
    google_login_page.open()
    google_login_page.click_on("google-email-field")
    autofill_popup.ensure_autofill_dropdown_visible()

    first_credential = autofill_popup.get_nth_element("1")
    assert autofill_popup.get_primary_value(first_credential) == USERNAME

    # 4. Save a couple more credential sets and verify they are visible in about:logins
    about_logins.open()
    time.sleep(0.5)
    about_logins.add_login(GOOGLE_ORIGIN, USERNAME2, PASSWORD2)
    time.sleep(0.5)
    about_logins.add_login(GOOGLE_ORIGIN, USERNAME3, PASSWORD3)

    about_logins.open()
    assert USERNAME3 in about_logins.get_element("login-list").text

    # 5. Denied credentials are not saved
    about_logins.open()
    assert DENIED_USERNAME not in about_logins.get_element("login-list").text
    assert DENIED_PASSWORD not in about_logins.get_element("login-list").text

    # 6. Refresh login page again and click inside input box
    driver.delete_all_cookies()
    google_login_page.open()

    email_field = google_login_page.get_element("google-email-field")
    assert email_field.get_attribute("value") == ""

    google_login_page.click_on("google-email-field")
    autofill_popup.ensure_autofill_dropdown_visible()

    for i, expected_username in enumerate([USERNAME, USERNAME2, USERNAME3], start=1):
        credential = autofill_popup.get_nth_element(str(i))
        assert autofill_popup.get_primary_value(credential) == expected_username

    footer = autofill_popup.get_nth_element("5")
    assert autofill_popup.get_primary_value(footer) == "Manage Passwords"
