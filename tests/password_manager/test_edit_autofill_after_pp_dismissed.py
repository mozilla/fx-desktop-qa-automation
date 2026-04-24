import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object import AboutLogins, AboutPrefs, LoginAutofill
from modules.util import BrowserActions

CREDENTIAL_ORIGIN = "https://mozilla.github.io"
USERNAME = "username"
PASSWORD = "password"
PRIMARY_PASSWORD = "securePassword1"
ALERT_MESSAGE = "Primary Password successfully changed."
SECOND_USERNAME = "SecondUsername"
SECOND_PASSWORD = "secondPassword"


@pytest.fixture()
def test_case():
    return "2244618"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("signon.rememberSignons", True)]


def test_edit_autofill_after_pp_dismissed(driver: Firefox):
    """
    C2244618 - [PP] Verify that editing autofilled entries after PP was dismissed is possible
    """

    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    ba = BrowserActions(driver)
    tabs = TabBar(driver)
    about_logins = AboutLogins(driver)
    login_autofill = LoginAutofill(driver)
    nav = Navigation(driver)
    autofill_popup_panel = AutofillPopup(driver)

    # Have a Primary Password set
    about_prefs.create_primary_password(PRIMARY_PASSWORD, ALERT_MESSAGE, ba)

    # Open about:logins page and create a login entry
    tabs.open_and_switch_to_new_tab()
    about_logins.open()
    about_logins.add_login(CREDENTIAL_ORIGIN, USERNAME, PASSWORD)

    # Attempt to view the saved password in order to trigger the primary password prompt
    about_logins.element_visible("show-password-checkbox")
    about_logins.click_on("show-password-checkbox")

    # Dismiss the primary password prompt without entering the password
    about_logins.dismiss_pp_if_appears()

    # Go to the test website
    tabs.open_and_switch_to_new_tab()
    login_autofill.open()

    # Fill in both the username and password with new credentials and dismiss pp if appears
    login_form = LoginAutofill.LoginForm(login_autofill)
    login_form.fill_username(SECOND_USERNAME)
    about_logins.dismiss_pp_if_appears()
    login_form.fill_password(SECOND_PASSWORD)
    about_logins.dismiss_pp_if_appears()

    # Submit the form
    login_form.submit()

    # Fill in the correct primary password
    about_logins.enter_primary_password(PRIMARY_PASSWORD)

    # Click on the grey key icon, choose to save the credentials and reload the form
    nav.click_on("password-notification-key")
    autofill_popup_panel.click_doorhanger_button("save")
    login_autofill.open()

    # The credentials were saved and the autocomplete dropdown appear on page load with 2 entries.
    # (1 from preconditions and 1 for the newly saved credentials)
    login_autofill.click_on("username-login-field")
    autofill_popup_panel.verify_autocomplete_option(USERNAME)
    autofill_popup_panel.verify_autocomplete_option(SECOND_USERNAME)
