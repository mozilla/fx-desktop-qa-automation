import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import AutofillPopup
from modules.page_object import AboutLogins, GenericPage

LOGIN_URL = (
    "https://login.taobao.com/havanaone/login/login.htm"
    "?bizName=taobao"
    "&spm=a21wu.241046-global.754894437.1.41cab6cbIIlC3k"
    "&f=top"
    "&redirectURL=https%3A%2F%2Fworld.taobao.com%2F"
)
TAOBAO_ORIGIN = "https://login.taobao.com/"
TAOBAO_TITLE = "login.taobao.com"

USERNAME_1 = "fx_taobao_user_1"
PASSWORD_1 = "fx_taobao_pass_1"

USERNAME_2 = "fx_taobao_user_2"
PASSWORD_2 = "fx_taobao_pass_2"

DENIED_USERNAME = "fx_taobao_denied_user"
DENIED_PASSWORD = "fx_taobao_denied_pass"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("signon.rememberSignons", True),
        ("signon.autofillForms", True),
    ]


@pytest.fixture()
def temp_selectors():
    return {
        "username-field": {
            "selectorData": "fm-login-id",
            "strategy": "id",
            "groups": [],
        },
        "password-field": {
            "selectorData": "fm-login-password",
            "strategy": "id",
            "groups": [],
        },
        "consent-dialog-ok-button": {
            "selectorData": "button.dialog-btn.dialog-btn-ok",
            "strategy": "css",
            "groups": ["doNotCache"],
        },
        "consent-dialog-cancel-button": {
            "selectorData": "button.dialog-btn.dialog-btn-cancel",
            "strategy": "css",
            "groups": ["doNotCache"],
        },
    }


@pytest.fixture()
def test_case():
    return "2245425"


def get_taobao_logins(about_logins: AboutLogins):
    return [
        login
        for login in about_logins.get_elements("login-list-item")
        if login.get_attribute("title") == TAOBAO_TITLE
    ]


def dismiss_taobao_consent_with_escape_if_present(web_page: GenericPage):
    try:
        web_page.element_visible("consent-dialog-ok-button")
    except TimeoutException:
        return

    web_page.driver.switch_to.active_element.send_keys(Keys.ESCAPE)
    web_page.element_not_visible("consent-dialog-ok-button")


def open_taobao_login(driver: Firefox, temp_selectors: dict) -> GenericPage:
    web_page = GenericPage(driver, url=LOGIN_URL).open()
    web_page.elements |= temp_selectors

    web_page.element_visible("username-field")
    web_page.element_visible("password-field")

    dismiss_taobao_consent_with_escape_if_present(web_page)

    web_page.element_visible("username-field")
    web_page.element_visible("password-field")
    return web_page


@pytest.mark.headed
def test_taobao_login_autofill_dropdown(driver: Firefox, temp_selectors):
    """
    2245425: Verify that:
    1. A single saved Taobao credential autofills on page load.
    2. Multiple saved Taobao credentials are stored in about:logins.
    3. Dismissed save-password prompts do not create extra saved logins.
    4. With multiple saved logins, fields are not autofilled on load and
       the autocomplete dropdown is displayed on field focus together with
       the saved credentials and the Manage Passwords entry.
    """
    about_logins = AboutLogins(driver)
    autofill_popup = AutofillPopup(driver)

    # Step 1: open login page
    open_taobao_login(driver, temp_selectors)

    # Step 2: add first credential in about:logins
    about_logins.open()
    original_logins_amount = len(about_logins.get_elements("login-list-item"))
    about_logins.add_login(TAOBAO_ORIGIN, USERNAME_1, PASSWORD_1)

    about_logins.wait.until(
        lambda _: (
            len(about_logins.get_elements("login-list-item")) > original_logins_amount
        )
    )

    taobao_logins = get_taobao_logins(about_logins)
    assert taobao_logins

    # Step 3: refresh page and verify autofill works
    web_page = open_taobao_login(driver, temp_selectors)

    web_page.wait.until(
        lambda _: web_page.get_element("username-field").get_attribute("value")
        == USERNAME_1
    )
    web_page.wait.until(
        lambda _: web_page.get_element("password-field").get_attribute("value")
        == PASSWORD_1
    )

    # Step 4: add second credential for same origin
    about_logins.open()
    original_logins_amount = len(about_logins.get_elements("login-list-item"))
    about_logins.add_login(TAOBAO_ORIGIN, USERNAME_2, PASSWORD_2)

    about_logins.wait.until(
        lambda _: (
            len(about_logins.get_elements("login-list-item")) > original_logins_amount
        )
    )

    taobao_logins = get_taobao_logins(about_logins)
    assert len(taobao_logins) >= 2

    # Step 5: input another credential set
    web_page = open_taobao_login(driver, temp_selectors)

    web_page.fill("username-field", DENIED_USERNAME, press_enter=False)
    web_page.fill("password-field", DENIED_PASSWORD, press_enter=False)
    web_page.get_element("password-field").send_keys(Keys.ENTER)

    about_logins.open()
    taobao_logins = get_taobao_logins(about_logins)
    assert len(taobao_logins) == 2

    # Step 6: refresh again and verify:
    # - fields are not autofilled on load
    # - dropdown is displayed on focus
    # - saved credentials are listed
    # - Manage Passwords footer is present
    web_page = open_taobao_login(driver, temp_selectors)

    web_page.wait.until(
        lambda _: web_page.get_element("username-field").get_attribute("value") == ""
    )
    web_page.wait.until(
        lambda _: web_page.get_element("password-field").get_attribute("value") == ""
    )

    web_page.click_on("username-field")
    autofill_popup.ensure_autofill_dropdown_visible()

    first_value = autofill_popup.get_primary_value(autofill_popup.get_nth_element(1))
    second_value = autofill_popup.get_primary_value(autofill_popup.get_nth_element(2))
    footer_value = autofill_popup.get_primary_value(autofill_popup.get_nth_element(3))

    assert {first_value, second_value} == {USERNAME_1, USERNAME_2}
    assert footer_value == "Manage Passwords"
