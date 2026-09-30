import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutConfig, AboutPrefs

TRR_MODE_PREF = "network.trr.mode"
TRR_MODE_DOH_ONLY = 3


@pytest.fixture()
def test_case():
    return "499033"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.aboutConfig.showWarning", False)]


def test_trr_mode_set_to_3(driver: Firefox):
    """
    C499033 - Verify that network.trr.mode value set to 3 works correctly.
    """
    # Instantiate objects
    about_config = AboutConfig(driver)
    prefs = AboutPrefs(driver, category="privacy")

    # Set network.trr.mode to 3 in about:config
    about_config.edit_config_value(TRR_MODE_PREF, TRR_MODE_DOH_ONLY)

    # Open preferences and search for Secure DNS
    prefs.open()
    prefs.find_in_settings("secure DNS")
    prefs.open_doh_advanced()

    # Expect "Custom" and "Always warn me if secure DNS isn't available" checkboxes checked
    prefs.element_has_attribute("doh-radio-custom-input", "checked")
    prefs.element_has_attribute("doh-fallback-checkbox-input", "checked")
