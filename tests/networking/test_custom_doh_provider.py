import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutConfig, AboutPrefs

QUAD9_URL = "https://dns.quad9.net/dns-query"
CUSTOM_PROVIDER_VALUE = "custom"
TRR_PREF = "network.trr.uri"


@pytest.fixture()
def test_case():
    return "545743"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.search.region", "US"),
        ("browser.aboutConfig.showWarning", False),
    ]


def test_custom_doh_provider(driver: Firefox):
    """
    C545743 - Verify that a custom DoH provider can be set in Custom mode
    """
    # Instantiate objects
    prefs = AboutPrefs(driver, category="privacy")
    about_config = AboutConfig(driver)

    # Open DoH Advanced section and switch to Custom mode
    prefs.open()
    prefs.open_doh_advanced()
    prefs.select_doh_protection_level("custom")

    # Choose the "Custom" provider option and enter a custom provider URL
    prefs.select_doh_provider(CUSTOM_PROVIDER_VALUE)
    prefs.set_custom_doh_provider(QUAD9_URL)

    # Verify network.trr.uri in about:config reflects the custom provider
    assert about_config.get_pref_value(TRR_PREF) == QUAD9_URL
