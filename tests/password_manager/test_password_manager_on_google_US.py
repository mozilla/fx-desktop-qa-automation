import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object import AboutLogins, GenericPage

GOOGLE_LOGIN_URL = "https://accounts.google.com/signin/v2/identifier?&passive=true&continue=https%3A%2F%2Fwww.google.com%2F&flowName=GlifWebSignIn&flowEntry=ServiceLogin"
GOOGLE_ORIGIN = "https://accounts.google.com"

USERNAME = "username1@gmail.com"
PASSWORD = "password1"
USERNAME2 = "username2@gmail.com"
PASSWORD2 = "password2"
USERNAME3 = "username3@gmail.com"
PASSWORD3 = "password3"


@pytest.fixture()
def test_case():
    return "NEW_TEST_CASE_ID"


@pytest.fixture()
def add_to_prefs_list():
    return [("signon.rememberSignons", True), ("signon.autofillForms", True)]


@pytest.fixture()
def temp_selectors():
    return {
        "google-email-field": {
            "selectorData": "identifierId",
            "strategy": "id",
            "groups": [],
        }
    }


def add_login_and_wait(about_logins, origin, username, password):
    original_count = len(about_logins.get_elements("login-list-item"))
    about_logins.add_login(origin, username, password)
    about_logins.wait.until(
        lambda _: len(about_logins.get_elements("login-list-item")) > original_count
    )


@pytest.mark.headed
def test_google_login_saved_credentials_dropdown(driver: Firefox, temp_selectors):
    """
    Verify that saved Google credentials are displayed in the autofill dropdown.
    """
    about_logins = AboutLogins(driver)
    autofill_popup = AutofillPopup(driver)

    about_logins.open()
    add_login_and_wait(about_logins, GOOGLE_ORIGIN, USERNAME, PASSWORD)
    add_login_and_wait(about_logins, GOOGLE_ORIGIN, USERNAME2, PASSWORD2)
    add_login_and_wait(about_logins, GOOGLE_ORIGIN, USERNAME3, PASSWORD3)

    google_login_page = GenericPage(driver, url=GOOGLE_LOGIN_URL).open()
    google_login_page.elements |= temp_selectors

    google_login_page.click_on("google-email-field")
    autofill_popup.ensure_autofill_dropdown_visible()

    for i, expected_username in enumerate([USERNAME, USERNAME2, USERNAME3], start=1):
        credential = autofill_popup.get_nth_element(str(i))
        assert autofill_popup.get_primary_value(credential) == expected_username

    passkey = autofill_popup.get_nth_element("4")
    assert autofill_popup.get_primary_value(passkey) == "Use a passkey"

    footer = autofill_popup.get_nth_element("5")
    assert autofill_popup.get_primary_value(footer) == "Manage Passwords"
