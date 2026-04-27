import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup, Navigation, TabBar
from modules.page_object import AboutLogins, LoginAutofill

EDIT_PASSWORD = "GG"
SECOND_EDIT_PASSWORD = "RR"


@pytest.fixture()
def test_case():
    return "2248179"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("signon.rememberSignons", True)]


def test_edit_generated_password_triggers_autosave(driver: Firefox):
    """
    C2248179 - Verify that editing a generated password triggers auto-save
    """

    # Instantiate objects
    login_autofill = LoginAutofill(driver)
    autofill_popup_panel = AutofillPopup(driver)
    nav = Navigation(driver)
    about_logins = AboutLogins(driver)
    tabs = TabBar(driver)

    # Navigate to a signup form
    login_autofill.open()

    # Generate a secure password
    login_autofill.click_on("password-signup-field")
    autofill_popup_panel.click_securely_generated_password()

    # A blue key icon is displayed on the left side of the address bar and "Password Saved!" message is also displayed
    nav.element_visible("password-notification-key")
    nav.element_visible("confirmation-hint")

    # Edit the generated password directly in the password field
    login_autofill.get_element("password-signup-field").send_keys(EDIT_PASSWORD)

    expected_password = login_autofill.get_element(
        "password-signup-field"
    ).get_attribute("value")

    # Focus away from the password field
    login_autofill.click_on("username-field")

    # A blue key icon is displayed on the left side of the address bar and "Password Saved!" message is also displayed
    nav.element_visible("password-notification-key")
    nav.element_visible("confirmation-hint")

    # Open about:logins, locate the entry for the above edited generated password and reveal password
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    about_logins.open()

    # Entry shows an empty username
    about_logins.element_attribute_contains(
        "about-logins-page-username-field", "placeholder", "(no username)"
    )

    # Entry shows edited password is saved
    about_logins.click_reveal_password_button()
    about_logins.assert_revealed_password(expected_password)

    # Go back to the password field tab and focus again the password field
    driver.switch_to.window(driver.window_handles[0])
    login_autofill.click_on("password-signup-field")
    autofill_popup_panel.click_autofill_form_option()

    # Make additional edits to the initial edited password
    login_autofill.get_element("password-signup-field").send_keys(SECOND_EDIT_PASSWORD)

    expected_password_updated = login_autofill.get_element(
        "password-signup-field"
    ).get_attribute("value")

    # Focus away from the password field
    login_autofill.click_on("username-field")

    # A blue key icon is displayed on the left side of the address bar and "Password Saved!" message is also displayed
    nav.element_visible("password-notification-key")
    nav.element_visible("confirmation-hint")

    # Go back to again about:logins
    driver.switch_to.window(driver.window_handles[1])
    about_logins.open()

    # Entry shows an empty username
    about_logins.element_attribute_contains(
        "about-logins-page-username-field", "placeholder", "(no username)"
    )

    # Entry shows edited password is saved
    about_logins.click_reveal_password_button()
    about_logins.assert_revealed_password(expected_password_updated)
