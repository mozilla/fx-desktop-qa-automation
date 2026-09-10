import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.page_object import AboutNetworking

TEST_URL = "https://www.wikipedia.org/"
TEST_HOST = "www.wikipedia.org"
UNREACHABLE_DOH_URL = "https://127.0.0.1:1/dns-query"


@pytest.fixture()
def test_case():
    return "463507"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("network.trr.mode", 2),
        ("network.trr.uri", UNREACHABLE_DOH_URL),
    ]


def test_doh_failure_falls_back_to_dns(driver: Firefox):
    """
    C463507 - Verify that requests which fail to connect to the DoH server
    are successfully handled by the DNS server instead.
    """
    # Instantiate objects
    networking = AboutNetworking(driver)
    tabs = TabBar(driver)

    # Trigger a DNS request while the configured DoH server is unreachable
    driver.get(TEST_URL)

    # Verify that Firefox falls back to the native DNS resolver
    tabs.open_and_switch_to_new_tab()

    networking.open()
    networking.select_network_category("dns")
    networking.wait_for_dns_entry(TEST_HOST, trr="false")
