import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object import AboutLogins, GenericPage


REDDIT_LOGIN_URL = "https://www.reddit.com/login/"
REDDIT_ORIGIN = "https://www.reddit.com"

USERNAME = "username1"
PASSWORD = "password1"
USERNAME2 = "username2"
PASSWORD2 = "password2"
USERNAME3 = "username3"
PASSWORD3 = "password3"

UNSAVED_USERNAME = "unsaved_user"
UNSAVED_PASSWORD = "unsaved_pass"


@pytest.fixture()
def test_case():
    return "2245451"


@pytest.fixture()
def add_to_prefs_list():
    return [("signon.rememberSignons", True), ("signon.autofillForms", True)]


@pytest.fixture()
def temp_selectors():
    return {
        "reddit-username-parent": {
            "selectorData": "auth-text-input[name='username']",
            "strategy": "css",
            "groups": ["doNotCache"],
        },
        "reddit-username-field": {
            "selectorData": "input[name='username']",
            "strategy": "css",
            "shadowParent": "reddit-username-parent",
            "groups": ["doNotCache"],
        },
        "reddit-password-parent": {
            "selectorData": "auth-text-input[name='password']",
            "strategy": "css",
            "groups": ["doNotCache"],
        },
        "reddit-password-field": {
            "selectorData": "input[name='password']",
            "strategy": "css",
            "shadowParent": "reddit-password-parent",
            "groups": ["doNotCache"],
        },
    }

def add_login_and_wait(about_logins, origin, username, password):
    about_logins.open()
    original_count = len(about_logins.get_elements("login-list-item"))
    about_logins.add_login(origin, username, password)
    about_logins.wait.until(
        lambda _: len(about_logins.get_elements("login-list-item")) > original_count
    )


@pytest.mark.headed
def test_reddit_login_autofill_and_storage(driver: Firefox, temp_selectors):
    """
    Verify Reddit credentials saving behavior and autofill dropdown.
    """

    about_logins = AboutLogins(driver)
    autofill_popup = AutofillPopup(driver)

    # Saving the credentials
    add_login_and_wait(about_logins, REDDIT_ORIGIN, USERNAME, PASSWORD)
    add_login_and_wait(about_logins, REDDIT_ORIGIN, USERNAME2, PASSWORD2)
    add_login_and_wait(about_logins, REDDIT_ORIGIN, USERNAME3, PASSWORD3)

    # Open Reddit login page and trigger autofill
    reddit_page = GenericPage(driver, url=REDDIT_LOGIN_URL)
    reddit_page.open()
    reddit_page.elements |= temp_selectors

    # IMPORTANT: wait + focus properly (React input)
    reddit_page.element_visible("reddit-username-field")
    reddit_page.click_on("reddit-username-field")

    # Type partial to trigger autofill
    reddit_page.fill("reddit-username-field", USERNAME[:3], press_enter=False)

    autofill_popup.ensure_autofill_dropdown_visible()

    for expected_username in [USERNAME, USERNAME2, USERNAME3]:
        autofill_popup.element_visible(
            "select-form-option-by-value", labels=[expected_username]
        )

    autofill_popup.element_visible(
        "select-form-option-by-value", labels=["Manage Passwords"]
    )

    # Negative case
    reddit_page.fill("reddit-username-field", UNSAVED_USERNAME, press_enter=False)

    autofill_popup.ensure_autofill_dropdown_visible()

    assert not autofill_popup.get_elements(
        "select-form-option-by-value", labels=[UNSAVED_USERNAME]
    ), "Unsaved credential should NOT appear in autofill"

    # Validate via about:logins
    about_logins.open()
    saved_logins = about_logins.get_elements("login-list-item")

    usernames = [login.text for login in saved_logins]

    assert any(USERNAME in u for u in usernames)
    assert any(USERNAME2 in u for u in usernames)
    assert any(USERNAME3 in u for u in usernames)

    assert not any(UNSAVED_USERNAME in u for u in usernames)