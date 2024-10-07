import pytest
import time

from selenium.webdriver import Firefox
from modules.page_object import AboutPrefs
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "2245178"


def test_add_primary_pw(driver: Firefox):
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
    is_disabled = about_prefs.get_element("current-pw").get_attribute("disabled")
    assert is_disabled

    # Primary password can be changed
    about_prefs.get_element("enter-new-pw").send_keys("securePassword1")
    about_prefs.get_element("reenter-new-pw").send_keys("securePassword1")
    about_prefs.click_on("submit-pw")

    # Check that the pop-up appears
    time.sleep(2)
    with driver.context(driver.CONTEXT_CHROME):
        driver.switch_to.window(driver.window_handles[-1])
        assert driver.title == "Password Change Succeeded"
