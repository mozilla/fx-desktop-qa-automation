import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs

EXPECTED_PROVIDERS = ["Cloudflare", "NextDNS"]
REGION_CASE_IDS = {
    "RO": "2180318.1",
    "UK": "2180318.2",
    "SE": "2180318.3",
}


@pytest.fixture(params=REGION_CASE_IDS.keys())
def region(request):
    return request.param


@pytest.fixture()
def test_case(region):
    return REGION_CASE_IDS[region]


@pytest.fixture()
def add_to_prefs_list(region):
    return [
        ("browser.search.region", region),
        ("doh-rollout.home-region", region),
    ]


def test_doh_providers_ro_uk_se_regions(driver: Firefox):
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
