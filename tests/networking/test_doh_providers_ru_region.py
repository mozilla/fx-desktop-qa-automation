import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs

EXPECTED_PROVIDERS = ["Cloudflare"]


@pytest.fixture()
def test_case():
    return "2180315"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.search.region", "RU"),
        ("doh-rollout.home-region", "RU"),
    ]


def test_doh_providers_ru_region(driver: Firefox):
    """
    C2180315 - Verify only Cloudflare provider is displayed in RU region.
    """
    # Instantiate objects
    prefs = AboutPrefs(driver, category="privacy")

    # Select Custom DoH mode and verify Cloudflare is the only provider
    prefs.open()
    prefs.open_doh_advanced()
    prefs.select_doh_protection_level("custom")
    prefs.verify_doh_providers_displayed(EXPECTED_PROVIDERS)
