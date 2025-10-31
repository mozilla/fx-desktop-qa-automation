import pytest
from selenium.webdriver import Firefox

from modules.page_object_about_pages import AboutLogins
from modules.page_object_autofill import LoginAutofill

TEST_PAGE_URL = "https://mozilla.github.io/form-fill-examples/password_manager/login_and_pw_change_forms.html"
USERNAME = "username1"
PASSWORD = "dp@ssw0r"


@pytest.fixture()
def test_case():
    return "2241089"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("signon.rememberSignons", True), ("signon.autofillForms", True)]


def test_saved_hyperlink_redirects_to_corresponding_page(driver: Firefox):
    """
    C2241089 - Verify that a saved hyperlink redirects to the corresponding page
    """
    # Instantiate objects
    about_logins = AboutLogins(driver)
    login_autofill = LoginAutofill(driver)

    # Add a new login
    about_logins.open()
    about_logins.add_login(TEST_PAGE_URL, USERNAME, PASSWORD)

    # Wait for item to populate login list
    about_logins.wait.until(
        lambda _: "initialized"
        in about_logins.get_element("login-list").get_attribute("class")
    )
    # Click on the hyperlink website
    about_logins.click_on("website-address")
    about_logins.switch_to_new_tab()
    about_logins.url_contains("mozilla.github")

    # Creating an instance of the LoginForm within the LoginAutofill page object
    login_autofill.open()
    login_form = LoginAutofill.LoginForm(login_autofill)

    # Verify the username field has the saved value
    login_form.verify_username_value(USERNAME)

    # Verify the password field is filled with a value that match the length of the saved password
    password_element = login_form.verify_password_length(8)
    assert len(password_element.get_attribute("value")) == 8
