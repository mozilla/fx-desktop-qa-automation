import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutConfig, AboutPrefs

NEXTDNS_URL = "https://firefox.dns.nextdns.io/"
TRR_URI_PREF = "network.trr.uri"
NEXTDNS_LABEL = "NextDNS"


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
    C545742 - Verify that NextDNS can be selected as DoH provider
    """
    # Instantiate objects
    prefs = AboutPrefs(driver, category="privacy")
    about_config = AboutConfig(driver)

    # Open about:preferences and select Increased Protection in the DNS over HTTPS section
    prefs.open()
    prefs.select_doh_protection_level("increased-protection")
    prefs.element_attribute_is("doh-increased-protection-radio", "selected", "true")

    # Select NextDNS from the resolver dropdown
    prefs.select_doh_provider(NEXTDNS_LABEL)
    prefs.element_attribute_is("doh-enabled-resolver", "label", NEXTDNS_LABEL)

    # Navigate away and back to verify the selection persists without errors
    driver.get("about:blank")
    prefs.open()
    prefs.element_attribute_is("doh-enabled-resolver", "label", NEXTDNS_LABEL)

    # Verify network.trr.uri in about:config
    assert about_config.get_pref_value(TRR_URI_PREF) == NEXTDNS_URL
