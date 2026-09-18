import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs

EXPECTED_PROVIDERS = ["CIRA Canadian Shield", "Cloudflare", "NextDNS"]


@pytest.fixture()
def test_case():
    return "2180317"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.search.region", "CA"),
        ("doh-rollout.home-region", "CA"),
        ("browser.aboutConfig.showWarning", False),
    ]


def test_doh_provider_ca_region(driver: Firefox):
    """
    C2180317 - Verify all 3 providers cira-CA, cloudflare-global and nextdns-global are displayed in ca region.
    """
    # Instantiate objects
    prefs = AboutPrefs(driver, category="privacy")

    # Select Custom DoH mode and verify there 3 expected providers displayed
    prefs.open()
    prefs.open_doh_advanced()
    prefs.select_doh_protection_level("custom")
    prefs.verify_doh_providers_displayed(EXPECTED_PROVIDERS)
