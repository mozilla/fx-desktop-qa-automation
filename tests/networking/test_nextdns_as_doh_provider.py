import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutConfig, AboutPrefs

NEXTDNS_URL = "https://firefox.dns.nextdns.io/"
TRR_PREF = "network.trr.uri"


@pytest.fixture()
def test_case():
    return "545742"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.search.region", "US"),
        ("browser.aboutConfig.showWarning", False),
    ]


def test_nextdns_as_doh_provider(driver: Firefox):
    """
    C545742 - Verify that NextDNS can be set as the DoH provider in Custom mode
    """
    # Instantiate objects
    prefs = AboutPrefs(driver, category="privacy")
    about_config = AboutConfig(driver)

    # Open DoH Advanced sub-pane and switch to Custom mode (provider menu only shows here)
    prefs.open()
    prefs.open_doh_advanced()
    prefs.select_doh_protection_level("custom")

    # Select NextDNS from the provider dropdown and verify status box reflects it
    prefs.select_doh_provider(NEXTDNS_URL)
    prefs.verify_doh_provider("NextDNS")

    # Verify network.trr.uri in about:config
    assert about_config.get_pref_value(TRR_PREF) == NEXTDNS_URL
