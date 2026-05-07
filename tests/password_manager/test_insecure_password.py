import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait

from modules.browser_object import AutofillPopup
from modules.page_object_autofill import LoginAutofill
from modules.page_object_generics import GenericPage

TESTFIRE_LOGIN_URL = "http://demo.testfire.net/login.jsp"
INSECURE_WARNING_TEXT = "This connection is not secure."
MANAGE_PASSWORDS_TEXT = "Manage Passwords"
SUPPORT_PAGE_URL_PART = "support.mozilla.org"
SUPPORT_PAGE_ARTICLE_PART = "insecure-password-warning-firefox"


@pytest.fixture()
def test_case():
    return "2246548"


@pytest.fixture()
def add_to_prefs_list():
    return [("signon.rememberSignons", True)]


def get_autofill_dropdown_values(autofill_popup: AutofillPopup) -> list[str]:
    autofill_popup.ensure_autofill_dropdown_visible()
    return [
        autofill_popup.get_primary_value(option)
        for option in autofill_popup.get_elements("select-form-option")
    ]


def verify_insecure_warning_dropdown(autofill_popup: AutofillPopup):
    autofill_popup.ensure_autofill_dropdown_visible()
    autofill_popup.element_visible("insecure-login-warning")
    autofill_popup.element_visible("insecure-login-warning-text")
    autofill_popup.element_visible("manage-passwords")


def test_insecure_login_contextual_warning(driver: Firefox):
    """
    C2246548 - Verify insecure contextual warning is shown for HTTP login fields.
    Test redirects to support article and about:logins when clicking on the respective options in the dropdown.
    """

    autofill_popup = AutofillPopup(driver)
    login_autofill = LoginAutofill(driver)

    GenericPage(driver, url=TESTFIRE_LOGIN_URL).open()

    login_autofill.element_clickable("testfire-username-field")
    login_autofill.click_on("testfire-username-field")

    verify_insecure_warning_dropdown(autofill_popup)

    initial_tabs = driver.window_handles
    autofill_popup.select_nth_element(1)

    WebDriverWait(driver, 10).until(
        lambda _: len(driver.window_handles) > len(initial_tabs)
    )
    driver.switch_to.window(driver.window_handles[-1])

    WebDriverWait(driver, 10).until(
        lambda _: SUPPORT_PAGE_URL_PART in driver.current_url
    )
    assert SUPPORT_PAGE_URL_PART in driver.current_url
    assert SUPPORT_PAGE_ARTICLE_PART in driver.current_url

    driver.close()
    driver.switch_to.window(initial_tabs[0])

    login_autofill.element_clickable("testfire-username-field")
    login_autofill.click_on("testfire-username-field")
    login_autofill.click_on(
        "testfire-username-field"
    )  # Click twice so the dropdown appears

    verify_insecure_warning_dropdown(autofill_popup)

    initial_tabs = driver.window_handles

    autofill_popup.click_manage_passwords()

    driver.switch_to.window(driver.window_handles[-1])

    WebDriverWait(driver, 10).until(
        lambda _: driver.current_url.startswith("about:logins")
    )

    assert driver.current_url.startswith("about:logins")
