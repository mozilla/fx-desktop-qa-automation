import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.page_object import AboutConfig, AboutNetworking, AboutPrefs

TEST_URL = "https://www.facebook.com/"
TEST_HOST = "www.facebook.com"
TRR_MODE_PREF = "network.trr.mode"
DEFAULT_TRR_MODE = "0"
CUSTOM_NO_FALLBACK_TRR_MODE = "3"


@pytest.fixture()
def test_case():
    return "2180311"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.search.region", "US"),
        ("browser.aboutConfig.showWarning", False),
    ]


def test_doh_custom_no_fallback_allowed(driver: Firefox):
    """
    C2180311 - Verify that the user can set DOH to Custom with no fallback
    """
    # Instantiate objects
    prefs = AboutPrefs(driver, category="privacy")
    about_config = AboutConfig(driver)
    networking = AboutNetworking(driver)
    tabs = TabBar(driver)

    # Verify the network.trr.mode value is 0
    assert about_config.get_pref_value(TRR_MODE_PREF) == DEFAULT_TRR_MODE

    # Select Custom mode and check "Always warn me if secure DNS isn't available"
    prefs.open()
    prefs.open_doh_advanced()
    prefs.select_doh_protection_level("custom")
    prefs.set_doh_fallback_warning(True)

    # Reach www.facebook.com and verify the lookup is resolved via TRR
    driver.get(TEST_URL)
    tabs.open_and_switch_to_new_tab()
    networking.open()
    networking.select_network_category("dns")
    networking.wait_for_dns_entry(TEST_HOST, trr="true")

    # Clear cached elements before reusing about_config in the new tab
    about_config.clear_cache()

    # Verify the network.trr.mode value is set to 3
    assert about_config.get_pref_value(TRR_MODE_PREF) == CUSTOM_NO_FALLBACK_TRR_MODE
