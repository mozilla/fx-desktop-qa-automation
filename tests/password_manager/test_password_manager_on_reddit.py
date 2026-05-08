import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object import AboutLogins, GenericPage
from modules.page_object_autofill import LoginAutofill

REDDIT_LOGIN_URL = "https://www.reddit.com/login/"
REDDIT_ORIGIN = "https://www.reddit.com"

USERNAME = "username1"
PASSWORD = "password1"
USERNAME2 = "username2"
PASSWORD2 = "password2"
USERNAME3 = "username3"
PASSWORD3 = "password3"

EXPECTED_USERNAMES = [USERNAME, USERNAME2, USERNAME3]


@pytest.fixture()
def test_case():
    return "2245451"


@pytest.fixture()
def add_to_prefs_list():
    return [("signon.rememberSignons", True), ("signon.autofillForms", True)]


def add_login_and_wait(
    about_logins: AboutLogins, origin: str, username: str, password: str
):
    initial_login_count = len(about_logins.get_elements("login-list-item"))

    about_logins.add_login(origin, username, password)

    about_logins.expect(
        lambda _: (
            len(about_logins.get_elements("login-list-item")) == initial_login_count + 1
        )
    )


@pytest.mark.headed
def test_reddit_login_autofill_and_storage(driver: Firefox):
    """
    Verify Reddit saved credentials are shown in the Firefox autofill dropdown
    and that selecting one autofills the username and password fields.
    """

    about_logins = AboutLogins(driver)
    autofill_popup = AutofillPopup(driver)

    about_logins.open()
    add_login_and_wait(about_logins, REDDIT_ORIGIN, USERNAME, PASSWORD)
    add_login_and_wait(about_logins, REDDIT_ORIGIN, USERNAME2, PASSWORD2)
    add_login_and_wait(about_logins, REDDIT_ORIGIN, USERNAME3, PASSWORD3)

    GenericPage(driver, url=REDDIT_LOGIN_URL).open()

    login_autofill = LoginAutofill(driver)

    login_autofill.element_clickable("reddit-username-field")
    login_autofill.click_on("reddit-username-field")
    login_autofill.fill("reddit-username-field", USERNAME[:3], press_enter=False)

    autofill_popup.ensure_autofill_dropdown_visible()

    dropdown_values = [
        autofill_popup.get_primary_value(autofill_popup.get_nth_element(index))
        for index in range(1, 4)
    ]

    assert set(EXPECTED_USERNAMES).issubset(dropdown_values)

    autofill_popup.select_nth_element(1)

    login_autofill.element_attribute_contains(
        "reddit-username-field", "value", USERNAME
    )

    login_autofill.click_on("reddit-password-field")
    autofill_popup.ensure_autofill_dropdown_visible()

    password_dropdown_values = [
        autofill_popup.get_primary_value(autofill_popup.get_nth_element(index))
        for index in range(1, 4)
    ]

    assert set(EXPECTED_USERNAMES).issubset(password_dropdown_values)

    autofill_popup.select_nth_element(1)

    login_autofill.element_attribute_contains(
        "reddit-password-field", "value", PASSWORD
    )
