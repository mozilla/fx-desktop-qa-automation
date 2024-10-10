import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from modules.page_object import AboutPrefs
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "2245178"


@pytest.fixture()
def hard_quit():
    return True


def test_add_primary_password(driver: Firefox):
    """
    C2245178: Verify that a primary password can be added in about:preferences#privacy
    """
    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy").open()
    ba = BrowserActions(driver)

    # Select the "Use a primary password" check box to trigger the "Change Primary Password" window
    about_prefs.click_on("use-primary-password")
    primary_pw_popup = about_prefs.get_element("browser-popup")
    ba.switch_to_iframe_context(primary_pw_popup)

    # Current password field is empty and cannot be changed
    about_prefs.element_attribute_contains("current-password", "disabled", "true")

    # Primary password can be changed
    about_prefs.get_element("enter-new-password").send_keys("securePassword1")
    about_prefs.get_element("reenter-new-password").send_keys("securePassword1")
    about_prefs.click_on("submit-password")

    # Check that the pop-up appears
    with driver.context(driver.CONTEXT_CHROME):
        about_prefs.wait_for_num_tabs(2)
        driver.switch_to.window(driver.window_handles[-1])
        passed = False
        try:
            assert driver.title == "Password Change Succeeded"
            passed = True
        finally:
            about_prefs.actions.send_keys(Keys.ENTER).perform()
        assert passed, "Password change success popup never appeared"
