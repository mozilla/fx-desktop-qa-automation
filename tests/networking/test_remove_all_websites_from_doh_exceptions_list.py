import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.page_object import AboutNetworking, AboutPrefs, GenericPage


@pytest.fixture()
def test_case():
    return "2180314"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("doh-rollout.home-region", "US"),
        ("doh-rollout.mode", 2),
    ]


EXCEPTION_SITES = {
    "facebook.com": ("https://www.facebook.com/", "www.facebook.com"),
    "example.com": ("https://example.com/", "example.com"),
    "mozilla.org": ("https://www.mozilla.org/", "www.mozilla.org"),
}


def test_remove_all_websites_from_doh_exceptions(driver: Firefox):
    """
    C2180314 - Verify that the user can remove all websites from the DoH exceptions list
    """
    # Instantiate objects
    prefs = AboutPrefs(driver, category="privacy")
    networking = AboutNetworking(driver)
    tabs = TabBar(driver)

    # Add a few websites to the DoH exceptions list
    prefs.open()
    for domain in EXCEPTION_SITES:
        prefs.open_doh_exceptions_dialog()
        prefs.add_doh_exception(domain)

    # Remove all websites from the DoH exceptions list
    prefs.open_doh_exceptions_dialog()
    prefs.remove_all_doh_exceptions()

    # Verify every host was resolved by TRR now that all exceptions were removed
    for url, host in EXCEPTION_SITES.values():
        tabs.open_and_switch_to_new_tab()
        GenericPage(driver, url=url).open()
        networking.open()
        networking.select_network_category("dns")
        networking.wait_for_dns_entry(host, trr="true")
