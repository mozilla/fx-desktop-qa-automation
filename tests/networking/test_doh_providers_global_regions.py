import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs

EXPECTED_PROVIDERS = ["Cloudflare", "NextDNS"]
REGIONS = ["RO", "UK", "SE"]


@pytest.fixture()
def test_case():
    return "2180318"


@pytest.fixture()
def add_to_prefs_list(region: str):
    return [
        ("browser.search.region", region),
        ("doh-rollout.home-region", region),
    ]


@pytest.mark.parametrize("region", REGIONS)
def test_doh_providers_global_regions(driver: Firefox, region: str):
    """
    C2180318 - Verify the Cloudflare and NextDNS providers are displayed for RO, UK, SE regions.
    """
    # Instantiate objects
    prefs = AboutPrefs(driver, category="privacy")

    # Select Custom DoH mode and verify both providers are displayed
    prefs.open()
    prefs.open_doh_advanced()
    prefs.select_doh_protection_level("custom")
    prefs.verify_doh_providers_displayed(EXPECTED_PROVIDERS)
