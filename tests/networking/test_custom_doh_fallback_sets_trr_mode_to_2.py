import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutConfig, AboutPrefs

TRR_MODE_PREF = "network.trr.mode"
DEFAULT_TRR_MODE = "0"
CUSTOM_FALLBACK_TRR_MODE = "2"


@pytest.fixture()
def test_case():
    return "500827"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.search.region", "US"),
        ("browser.aboutConfig.showWarning", False),
    ]


def test_custom_doh_fallback_sets_network_trr_mode_to_2(driver: Firefox):
    """
    C500827 - Verify that Custom DoH fallback sets network.trr.mode to 2
    """
    # Instantiate objects
    prefs = AboutPrefs(driver, category="privacy")
    about_config = AboutConfig(driver)

    # Verify the network.trr.mode value is 0
    assert about_config.get_pref_value(TRR_MODE_PREF) == DEFAULT_TRR_MODE

    # Select Custom mode and uncheck "Always warn me if secure DNS isn't available" option
    prefs.open()
    prefs.open_doh_advanced()
    prefs.select_doh_protection_level("custom")
    prefs.uncheck_doh_fallback_warning()

    # Verify the network.trr.mode value is set to 2
    assert about_config.get_pref_value(TRR_MODE_PREF) == CUSTOM_FALLBACK_TRR_MODE
