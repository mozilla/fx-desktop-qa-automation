import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import AutofillPopup
from modules.page_object import AboutLogins, GenericPage

LOGIN_URL = "https://www.facebook.com/login/device-based/regular/login/"
FACEBOOK_ORIGIN = "https://www.facebook.com/"
FACEBOOK_TITLE = "facebook.com"

USERNAME_1 = "fx_facebook_user_1"
PASSWORD_1 = "fx_facebook_pass_1"

USERNAME_2 = "fx_facebook_user_2"
PASSWORD_2 = "fx_facebook_pass_2"

DENIED_USERNAME = "fx_facebook_denied_user"
DENIED_PASSWORD = "fx_facebook_denied_pass"


@pytest.fixture()
def test_case():
    return "2245445"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("signon.rememberSignons", True),
        ("signon.autofillForms", True),
    ]


@pytest.fixture()
def temp_selectors():
    return {
        "facebook-username-field": {
            "selectorData": "input[name='email']",
            "strategy": "css",
            "groups": ["doNotCache"],
        },
        "facebook-password-field": {
            "selectorData": "input[name='pass']",
            "strategy": "css",
            "groups": ["doNotCache"],
        },
        "facebook-cookie-dialog": {
            "selectorData": (
                "//div[@role='dialog'][.//text()[contains(.,'cookies') or contains(.,'Cookies')]]"
            ),
            "strategy": "xpath",
            "groups": ["doNotCache"],
        },
        "facebook-cookie-decline": {
            "selectorData": (
                "//div[@role='dialog']//*[self::button or @role='button']"
                "[contains(normalize-space(.),'Decline optional cookies') "
                "or contains(normalize-space(.),'Only allow essential cookies')]"
            ),
            "strategy": "xpath",
            "groups": ["doNotCache"],
        },
        "facebook-cookie-allow": {
            "selectorData": (
                "//div[@role='dialog']//*[self::button or @role='button']"
                "[contains(normalize-space(.),'Allow all cookies') "
                "or contains(normalize-space(.),'Accept all cookies')]"
            ),
            "strategy": "xpath",
            "groups": ["doNotCache"],
        },
    }


def get_facebook_logins(about_logins: AboutLogins):
    return [
        login
        for login in about_logins.get_elements("login-list-item")
        if login.get_attribute("title") == FACEBOOK_TITLE
    ]


def open_facebook_login(driver: Firefox, temp_selectors: dict) -> GenericPage:
    web_page = GenericPage(driver, url=LOGIN_URL).open()
    web_page.elements |= temp_selectors

    web_page.element_visible("facebook-username-field")
    web_page.element_visible("facebook-password-field")


def dismiss_facebook_cookies_if_present(web_page: GenericPage):
    if len(web_page.get_elements("facebook-cookie-dialog")) == 0:
        return

    decline_buttons = web_page.get_elements("facebook-cookie-decline")
    allow_buttons = web_page.get_elements("facebook-cookie-allow")

    if decline_buttons:
        web_page.driver.execute_script("arguments[0].click();", decline_buttons[0])
    elif allow_buttons:
        web_page.driver.execute_script("arguments[0].click();", allow_buttons[0])
    else:
        return

    web_page.wait.until(
        lambda _: len(web_page.get_elements("facebook-cookie-dialog")) == 0
    )


def open_facebook_login(driver: Firefox, temp_selectors: dict) -> GenericPage:
    web_page = GenericPage(driver, url=LOGIN_URL).open()
    web_page.elements |= temp_selectors

    web_page.element_visible("facebook-username-field")
    web_page.element_visible("facebook-password-field")

    dismiss_facebook_cookies_if_present(web_page)

    web_page.element_visible("facebook-username-field")
    web_page.element_visible("facebook-password-field")
    return web_page


@pytest.mark.headed
def test_facebook_login_autofill_dropdown(driver: Firefox, temp_selectors):
    """
    2245445: Verify that:
    1. A single saved Facebook credential autofills on page load.
    2. Multiple saved Facebook credentials are stored in about:logins.
    3. Additional typed credentials are not saved.
    4. With multiple saved logins, fields are not autofilled on load and
       the autocomplete dropdown is displayed on field focus together with
       the saved credentials and the Manage Passwords entry.
    """
    about_logins = AboutLogins(driver)
    autofill_popup = AutofillPopup(driver)

    # Step 1: open login page
    open_facebook_login(driver, temp_selectors)

    # Step 2: add first credential in about:logins
    about_logins.open()
    original_logins_amount = len(about_logins.get_elements("login-list-item"))
    about_logins.add_login(FACEBOOK_ORIGIN, USERNAME_1, PASSWORD_1)

    about_logins.wait.until(
        lambda _: (
            len(about_logins.get_elements("login-list-item")) > original_logins_amount
        )
    )

    facebook_logins = get_facebook_logins(about_logins)
    assert facebook_logins

    # Step 3: refresh page and verify autofill works
    web_page = open_facebook_login(driver, temp_selectors)

    web_page.wait.until(
        lambda _: web_page.get_element("facebook-username-field").get_attribute("value")
        == USERNAME_1
    )
    web_page.wait.until(
        lambda _: web_page.get_element("facebook-password-field").get_attribute("value")
        == PASSWORD_1
    )

    # Step 4: add second credential for same origin
    about_logins.open()
    original_logins_amount = len(about_logins.get_elements("login-list-item"))
    about_logins.add_login(FACEBOOK_ORIGIN, USERNAME_2, PASSWORD_2)

    about_logins.wait.until(
        lambda _: (
            len(about_logins.get_elements("login-list-item")) > original_logins_amount
        )
    )

    facebook_logins = get_facebook_logins(about_logins)
    assert len(facebook_logins) >= 2

    # Step 5: input another credential set
    web_page = open_facebook_login(driver, temp_selectors)

    web_page.fill("facebook-username-field", DENIED_USERNAME, press_enter=False)
    web_page.fill("facebook-password-field", DENIED_PASSWORD, press_enter=False)
    web_page.get_element("facebook-password-field").send_keys(Keys.ENTER)

    about_logins.open()
    facebook_logins = get_facebook_logins(about_logins)
    assert len(facebook_logins) == 2

    # Step 6: refresh again and verify:
    # - fields are not autofilled on load
    # - dropdown is displayed on focus
    # - saved credentials are listed
    # - Manage Passwords footer is present
    web_page = open_facebook_login(driver, temp_selectors)

    web_page.wait.until(
        lambda _: web_page.get_element("facebook-username-field").get_attribute("value")
        == ""
    )
    web_page.wait.until(
        lambda _: web_page.get_element("facebook-password-field").get_attribute("value")
        == ""
    )

    username_field = web_page.get_element("facebook-username-field")

    web_page.click_on("facebook-username-field")
    username_field.send_keys(Keys.ARROW_DOWN)

    autofill_popup.ensure_autofill_dropdown_visible()

    first_value = autofill_popup.get_primary_value(autofill_popup.get_nth_element(1))
    second_value = autofill_popup.get_primary_value(autofill_popup.get_nth_element(2))
    footer_value = autofill_popup.get_primary_value(autofill_popup.get_nth_element(3))

    assert {first_value, second_value} == {USERNAME_1, USERNAME_2}
    assert footer_value == "Manage Passwords"
