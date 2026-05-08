import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait

from modules.browser_object import AutofillPopup
from modules.page_object_about_pages import AboutLogins
from modules.page_object_autofill import LoginAutofill
from modules.page_object_generics import GenericPage

TESTFIRE_LOGIN_URL = "http://demo.testfire.net/login.jsp"
SUPPORT_PAGE_URL_PART = "support.mozilla.org"
SUPPORT_PAGE_ARTICLE_PART = "insecure-password-warning-firefox"


@pytest.fixture()
def test_case():
    return "2246548"


@pytest.fixture()
def temp_selectors():
    return {
        "testfire-username-field": {
            "strategy": "css",
            "selectorData": "input[name='uid']",
            "groups": ["doNotCache"],
        }
    }


@pytest.fixture()
def add_to_prefs_list():
    return [("signon.rememberSignons", True)]


def verify_insecure_warning_dropdown(autofill_popup: AutofillPopup):
    autofill_popup.ensure_autofill_dropdown_visible()
    autofill_popup.element_visible("insecure-login-warning")
    autofill_popup.element_visible("insecure-login-warning-text")
    autofill_popup.element_visible("manage-passwords")


def open_insecure_warning_article(driver: Firefox, autofill_popup: AutofillPopup):
    initial_tabs = driver.window_handles

    autofill_popup.click_on("insecure-login-warning")

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


def open_manage_passwords(driver: Firefox, autofill_popup: AutofillPopup):
    initial_tabs = driver.window_handles

    autofill_popup.click_manage_passwords()

    WebDriverWait(driver, 10).until(
        lambda _: (
            driver.current_url.startswith(AboutLogins.URL_TEMPLATE)
            or len(driver.window_handles) > len(initial_tabs)
        )
    )

    if len(driver.window_handles) > len(initial_tabs):
        driver.switch_to.window(driver.window_handles[-1])

    WebDriverWait(driver, 10).until(
        lambda _: driver.current_url.startswith(AboutLogins.URL_TEMPLATE)
    )

    assert driver.current_url.startswith(AboutLogins.URL_TEMPLATE)


def test_insecure_login_contextual_warning(driver: Firefox, temp_selectors):
    """
    C2246548 - Verify insecure contextual warning is shown for HTTP login fields.
    Test redirects to support article and about:logins when clicking the respective
    options in the dropdown.
    """

    autofill_popup = AutofillPopup(driver)

    login_autofill = LoginAutofill(driver)
    login_autofill.elements |= temp_selectors

    page = GenericPage(driver, url=TESTFIRE_LOGIN_URL)
    page.elements |= temp_selectors
    page.open()

    login_autofill.element_clickable("testfire-username-field")
    login_autofill.click_on("testfire-username-field")
    login_autofill.click_on("testfire-username-field")

    verify_insecure_warning_dropdown(autofill_popup)
    open_insecure_warning_article(driver, autofill_popup)

    page.open()

    login_autofill.element_clickable("testfire-username-field")
    login_autofill.click_on("testfire-username-field")
    # make sure the dropdown is still there after clicking the username field
    login_autofill.fill("testfire-username-field", "", press_enter=False)

    verify_insecure_warning_dropdown(autofill_popup)
    open_manage_passwords(driver, autofill_popup)
