import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "446319"


def test_tcp_option_carries_over_private_window(driver: Firefox, panel_ui: PanelUi):
    """
    C446319 - Verify that the selected option carries over to Private window
    """

    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    normal_window = driver.current_window_handle

    # Select "Standard" up front: a fresh profile does not reliably start on it
    about_prefs.open()
    about_prefs.select_etp_level("standard")

    # Open a New private window
    panel_ui.open_and_switch_to_new_window("private")
    private_window = driver.current_window_handle
    private_about_prefs = AboutPrefs(driver, category="privacy")

    # Access about:preferences#privacy and observe the "Standard" section
    private_about_prefs.open()
    private_about_prefs.open_etp_settings()
    private_about_prefs.verify_etp_level("standard")

    # Click on the "Strict" option and open about:preferences#privacy in a normal window
    private_about_prefs.set_etp_level("strict")
    driver.switch_to.window(normal_window)
    about_prefs.open()

    # The "Strict" section is displayed
    about_prefs.open_etp_settings()
    about_prefs.verify_etp_level("strict")

    # Click on the "Custom" section and open about:preferences#privacy in a private window
    about_prefs.set_etp_level("custom")
    driver.switch_to.window(private_window)

    # about:preferences#privacy page is opened in private window
    private_about_prefs.open()

    # The "Custom" section is checked
    private_about_prefs.open_etp_settings()
    private_about_prefs.verify_etp_level("custom")
