import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.page_object import AboutConfig, AboutNetworking, AboutPrefs

TEST_URL = "https://www.facebook.com/"
TEST_HOST = "www.facebook.com"
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


def test_doh_custom_fallback_allowed(driver: Firefox):
    """
    C500827 - Verify that Custom DoH fallback is allowed
    """
    # Instantiate objects
    prefs = AboutPrefs(driver, category="privacy")
    about_config = AboutConfig(driver)
    networking = AboutNetworking(driver)
    tabs = TabBar(driver)

    # Verify the network.trr.mode value is 0
    assert about_config.get_pref_value(TRR_MODE_PREF) == DEFAULT_TRR_MODE

    # Check "Custom" and uncheck "Always warn me if secure DNS isn't available"
    prefs.open()
    prefs.open_doh_advanced()
    prefs.select_doh_protection_level("custom")
    prefs.set_doh_fallback_warning(False)

    # Reach www.facebook.com and verify the lookup is resolved via TRR
    driver.get(TEST_URL)
    tabs.open_and_switch_to_new_tab()
    networking.open()
    networking.select_network_category("dns")
    networking.wait_for_dns_entry(TEST_HOST, trr="true")

    # Clear cached elements before reusing about_config in the new tab
    about_config.clear_cache()

    # Verify the network.trr.mode value is set to 2
    assert about_config.get_pref_value(TRR_MODE_PREF) == CUSTOM_FALLBACK_TRR_MODE
