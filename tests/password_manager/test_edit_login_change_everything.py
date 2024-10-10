import pytest
from selenium.webdriver import Firefox

from modules.page_object_about_pages import AboutLogins

@pytest.fixture()
def test_case():
    return "2241121"

def test_edit_mode_change_everything(driver: Firefox):
    """
    C2241121 - Edit Mode - Change Everything
    """
    # Initialize page object and open AboutLogins page
    about_logins = AboutLogins(driver).open()

    # Click add login button
    about_logins.click_add_login_button()

    # Create initial test login data and add new login
    initial_login = {
        "origin": "test.mozilla.org",
        "username": "test_user",
        "password": "test_password123"
    }
    about_logins.create_new_login(initial_login)

    # Click Edit button through shadow DOM
    assert driver.execute_script("""
        const editButton = document.querySelector('login-item').shadowRoot.querySelector('edit-button').shadowRoot.querySelector('button.ghost-button');
        if (editButton) { editButton.click(); return true; }
        return false;
    """), "Edit button not found."

    # Update username
    updated_login = {
        "username": "updated_test_user",
        "password": "updated_password456"
    }
    assert driver.execute_script("""
        const inputField = document.querySelector('login-item').shadowRoot.querySelector('input[type="text"][name="username"]');
        if (inputField) {
            inputField.value = arguments[0];
            inputField.dispatchEvent(new Event('input', { bubbles: true }));
            return true;
        }
        return false;
    """, updated_login['username']), "Failed to update username field"

    # Update password
    assert driver.execute_script("""
        const passwordField = document.querySelector('login-item').shadowRoot.querySelector('input.password-display[type="password"]');
        if (passwordField) {
            passwordField.value = arguments[0];
            passwordField.dispatchEvent(new Event('input', { bubbles: true }));
            return true;
        }
        return false;
    """, updated_login['password']), "Failed to update password field"

    # Click Save button
    assert driver.execute_script("""
        const saveButton = document.querySelector('login-item').shadowRoot.querySelector('moz-button-group').querySelector('button.save-changes-button');
        if (saveButton) {
            saveButton.click();
            return true;
        }
        return false;
    """), "Save button not found."

    # Close browser session
    driver.quit()