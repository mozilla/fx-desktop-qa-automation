import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutConfig, AboutPrefs

CLOUDFLARE_URL = "https://mozilla.cloudflare-dns.com/dns-query"
TRR_PREF = "network.trr.default_provider_uri"


@pytest.fixture()
def test_case():
    return "545741"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.search.region", "US"),
        ("browser.aboutConfig.showWarning", False),
    ]


def test_cloudflare_default_doh_provider(driver: Firefox):
    """
    C545741 - Verify that Cloudflare set as default DoH provider
    """
    # Instantiate objects
    prefs = AboutPrefs(driver, category="privacy")
    about_config = AboutConfig(driver)

    # Select Default DoH mode and verify Cloudflare is the active provider
    prefs.open()
    prefs.select_doh_protection_level("default")
    prefs.verify_doh_provider("Cloudflare")

    # Verify network.trr.default_provider_uri in about:config
    assert about_config.get_pref_value(TRR_PREF) == CLOUDFLARE_URL
