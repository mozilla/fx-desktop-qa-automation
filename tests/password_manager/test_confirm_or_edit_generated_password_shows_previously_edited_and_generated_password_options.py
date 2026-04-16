import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.page_object_autofill import LoginAutofill

EDITED_PASSWORD = "T"


@pytest.fixture()
def test_case():
    return "2248183"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("signon.rememberSignons", True)]


def test_confirm_or_edit_generated_password_shows_previously_edited_and_generated_password_options(
    driver: Firefox,
):
    """
    C2248183 - Verify that the “Confirm/Retype Password” field autocomplete dropdown displays the previously edited
     and auto-saved generated password
    """

    # Instantiate objects
    login_autofill = LoginAutofill(driver)
    autofill_popup_panel = AutofillPopup(driver)
    panel = PanelUi(driver)
    nav = Navigation(driver)

    # Access a website with a signup page
    login_autofill.open()

    # Click on the password signup field and choose to "Use a Securely Generated" password
    login_autofill.click_on("password-signup-field")
    autofill_popup_panel.click_securely_generated_password()

    # A blue key icon is displayed on the left side of the address bar and "Password Saved!" message is also displayed
    nav.element_visible("password-notification-key")
    nav.element_visible("confirmation-hint")

    # Edit the generated password (e.g. add/remove characters) and click out-side of the field
    login_autofill.get_element("password-signup-field").send_keys(EDITED_PASSWORD)
    panel.click_outside_add_folder_panel()

    # A new “Password Saved!” blue message is displayed for every edit
    nav.element_visible("confirmation-hint")

    # Click on the Password field and clear its content
    login_autofill.get_element("password-signup-field").clear()

    # The autocomplete dropdown is displayed showing A "No username" entry
    login_autofill.click_on("password-signup-field")
    autofill_popup_panel.verify_autocomplete_option("No username")

    # The autocomplete dropdown is displayed "Use a Securely Generated Password" option
    autofill_popup_panel.verify_autocomplete_option("Use a Securely Generated Password")
