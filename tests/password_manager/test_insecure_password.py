import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object_autofill import LoginAutofill
from modules.page_object_generics import GenericPage

HTTP_LOGIN_URL = "http://the-internet.herokuapp.com/login"
SUPPORT_PAGE_URL_PART = "support.mozilla.org"
SUPPORT_PAGE_ARTICLE_PART = "insecure-password-warning-firefox"


@pytest.fixture()
def test_case():
    return "2246548"


@pytest.fixture()
def temp_selectors():
    return {
        "login-username-field": {
            "strategy": "css",
            "selectorData": "input[name='username']",
            "groups": ["doNotCache"],
        }
    }


@pytest.fixture()
def add_to_prefs_list():
    return [("signon.rememberSignons", True)]


def test_insecure_login_contextual_warning(driver: Firefox, temp_selectors):
    """
    C2246548 - Verify insecure contextual warning is shown for HTTP login fields.
    Test redirects to support article and about:logins when clicking the respective
    options in the dropdown.
    """

    def _verify_insecure_warning_dropdown():
        autofill_popup.ensure_autofill_dropdown_visible()
        autofill_popup.element_visible("insecure-login-warning")
        autofill_popup.element_visible("insecure-login-warning-text")
        autofill_popup.element_visible("manage-passwords")

    def _open_insecure_warning_article():
        initial_tab_count = len(driver.window_handles)

        autofill_popup.click_on("insecure-login-warning")

        page.wait_for_num_tabs(initial_tab_count + 1)
        driver.switch_to.window(driver.window_handles[-1])

        page.url_contains(SUPPORT_PAGE_URL_PART)
        page.url_contains(SUPPORT_PAGE_ARTICLE_PART)

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    def _open_manage_passwords():
        initial_tab_count = len(driver.window_handles)

        autofill_popup.click_manage_passwords()

        page.expect(
            lambda _: (
                "about:logins" in driver.current_url
                or len(driver.window_handles) == initial_tab_count + 1
            )
        )

        if len(driver.window_handles) == initial_tab_count + 1:
            driver.switch_to.window(driver.window_handles[-1])

        page.url_contains("about:logins")

    autofill_popup = AutofillPopup(driver)

    login_autofill = LoginAutofill(driver)
    login_autofill.elements |= temp_selectors

    page = GenericPage(driver, url=HTTP_LOGIN_URL)
    page.open()

    login_autofill.element_clickable("login-username-field")
    login_autofill.click_on("login-username-field")

    _verify_insecure_warning_dropdown()
    _open_insecure_warning_article()

    page.open()

    login_autofill.element_clickable("login-username-field")
    login_autofill.click_on("login-username-field")

    _verify_insecure_warning_dropdown()
    _open_manage_passwords()
