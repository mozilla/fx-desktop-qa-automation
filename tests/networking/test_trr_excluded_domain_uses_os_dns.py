import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutNetworking

TEST_URL = "https://www.wikipedia.org/"
TEST_HOST = "www.wikipedia.org"
CLOUDFLARE_DOH_URL = "https://mozilla.cloudflare-dns.com/dns-query"


@pytest.fixture()
def test_case():
    return "463622"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("network.trr.mode", 2),
        ("network.trr.uri", CLOUDFLARE_DOH_URL),
        ("network.trr.excluded-domains", TEST_HOST),
    ]


def test_trr_excluded_domain_uses_os_dns(driver: Firefox):
    """
    C463622 - Verify that domains that are part of the TRR user-defined exclusion list are handled by the OS DNS Server.
    """
    # Instantiate objects
    networking = AboutNetworking(driver)

    # Trigger a DNS request for a host in the TRR exclusion list
    driver.get(TEST_URL)

    # Verify the excluded host was resolved by the OS DNS resolver, not TRR
    networking.open()
    networking.select_network_category("dns")
    networking.wait_for_dns_entry(TEST_HOST, trr="false")
