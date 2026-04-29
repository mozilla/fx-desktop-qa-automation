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

    for expected_username in [USERNAME, USERNAME2, USERNAME3]:
        autofill_popup.element_visible(
            "select-form-option-by-value", labels=[expected_username]
        )

    autofill_popup.element_visible(
        "select-form-option-by-value", labels=["Use a passkey"]
    )

    autofill_popup.element_visible(
        "select-form-option-by-value", labels=["Manage Passwords"]
    )
