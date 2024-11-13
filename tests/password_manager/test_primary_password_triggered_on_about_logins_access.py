import pytest
from selenium.webdriver import Firefox, Keys
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import PanelUi, TabBar
from modules.page_object import AboutLogins, AboutPrefs
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "2245199"


def test_primary_password_triggered_on_about_logins_access_via_hamburger_menu(
    driver: Firefox,
):
    """
    C2245199: Verify that the primary password prompt is triggered on accessing about:logins through Hamburger Menu.

    Without restarting the browser after the primary password was set (limited action), Firefox does not
    trigger the primary password prompt when simply opening about:logins because no encrypted data is accessed
    initially. The prompt is triggered only when sensitive data, is accessed, requiring decryption.

    Once decrypted data has been accessed (e.g., showing a saved password), Firefox recognizes the need
    to protect further access to that data. As a result, subsequent navigation to about:logins will
    immediately trigger the primary password prompt to prevent unauthorized access to the decrypted source.
    """

    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy").open()
    ba = BrowserActions(driver)
    panel_ui = PanelUi(driver)
    tabs = TabBar(driver)
    about_logins = AboutLogins(driver)

    # Enable the setup for primary password
    about_prefs.click_on("use-primary-password")
    primary_pw_popup = about_prefs.get_element("browser-popup")
    ba.switch_to_iframe_context(primary_pw_popup)

    # Set primary password
    about_prefs.get_element("enter-new-password").send_keys("securePassword1")
    about_prefs.get_element("reenter-new-password").send_keys("securePassword1")
    about_prefs.click_on("submit-password")

    # Dismiss the success message after setting the primary password
    alert = about_prefs.get_alert()
    alert.accept()

    # Open about:logins page and create a login entry
    tabs.switch_to_new_tab()
    about_logins.open()
    about_logins.click_add_login_button()
    about_logins.create_new_login(
        {
            "origin": "mozilla.org",
            "username": "username",
            "password": "password",
        }
    )

    # Attempt to view the saved password in order to trigger the primary password prompt
    show_password = about_logins.get_element("show-password-checkbox")
    about_logins.expect(EC.element_to_be_clickable(show_password))
    about_logins.click_on(show_password)

    # Dismiss the primary password prompt without entering the password
    with driver.context(driver.CONTEXT_CHROME):
        driver.switch_to.window(driver.window_handles[-1])
        primary_password_prompt = about_logins.get_element("primary-password-prompt")
        primary_password_prompt.send_keys(Keys.ESCAPE)

    # Navigate to about:logins again through the hamburger menu
    tabs.switch_to_new_tab()
    panel_ui.open_panel_menu()
    panel_ui.redirect_to_about_logins_page()

    # Verify that the primary password prompt appears and enter the primary password
    with driver.context(driver.CONTEXT_CHROME):
        driver.switch_to.window(driver.window_handles[-1])
        # Fetch a fresh reference to avoid staling
        primary_password_prompt = about_logins.get_element("primary-password-prompt")
        assert primary_password_prompt.is_displayed()

        primary_password_input_field = about_logins.get_element(
            "primary-password-dialog-input-field"
        )
        primary_password_input_field.send_keys("securePassword1")
        primary_password_input_field.send_keys(Keys.ENTER)

    # Verify that about:logins page is accessible after the primary password was entered
    driver.switch_to.window(driver.window_handles[0])
    assert driver.current_url.startswith("about:logins")

    # Verify that the saved login is visible and accessible in the login list
    about_logins.wait.until(
        lambda _: about_logins.get_element("login-list-item").get_attribute("title")
        == "mozilla.org"
    )
