import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object import AboutLogins, GenericPage, LoginAutofill

REDDIT_LOGIN_URL = "https://www.reddit.com/login/"
REDDIT_ORIGIN = "https://www.reddit.com"

USERNAME = "username1"
PASSWORD = "password1"
USERNAME2 = "username2"
PASSWORD2 = "password2"
USERNAME3 = "username3"
PASSWORD3 = "password3"


@pytest.fixture()
def test_case():
    return "2245451"


@pytest.fixture()
def add_to_prefs_list():
    return [("signon.rememberSignons", True), ("signon.autofillForms", True)]


def add_login_and_wait(
    about_logins: AboutLogins, origin: str, username: str, password: str
):
    about_logins.open()
    initial_login_count = len(about_logins.get_elements("login-list-item"))

    about_logins.add_login(origin, username, password)

    about_logins.wait.until(
        lambda _: len(about_logins.get_elements("login-list-item"))
        == initial_login_count + 1
    )


@pytest.mark.headed
def test_reddit_login_autofill_and_storage(driver: Firefox):
    """
    Verify Reddit saved credentials are shown in the Firefox autofill dropdown.
    """

    about_logins = AboutLogins(driver)
    autofill_popup = AutofillPopup(driver)

    add_login_and_wait(about_logins, REDDIT_ORIGIN, USERNAME, PASSWORD)
    add_login_and_wait(about_logins, REDDIT_ORIGIN, USERNAME2, PASSWORD2)
    add_login_and_wait(about_logins, REDDIT_ORIGIN, USERNAME3, PASSWORD3)

    reddit_page = GenericPage(driver, url=REDDIT_LOGIN_URL)
    reddit_page.open()

    login_autofill = LoginAutofill(driver)

    login_autofill.element_clickable("reddit-username-field")
    login_autofill.click_on("reddit-username-field")
    login_autofill.fill("reddit-username-field", USERNAME[:3], press_enter=False)

    autofill_popup.ensure_autofill_dropdown_visible()

    for expected_username in [USERNAME, USERNAME2, USERNAME3]:
        autofill_popup.element_visible(
            "select-form-option-by-value", labels=[expected_username]
        )
