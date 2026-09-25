import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.page_object import AboutNetworking, AboutPrefs, GenericPage


@pytest.fixture()
def test_case():
    return "2180312"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("doh-rollout.home-region", "US"),
        ("doh-rollout.mode", 2),
    ]


EXCEPTION_DOMAIN = "facebook.com"
TEST_URL = "https://www.facebook.com/"
TEST_HOST = "www.facebook.com"


def test_add_website_to_doh_exceptions(driver: Firefox):
    """
    C2180312 - Verify that the user can add a website to the DoH exceptions list
    """
    # Instantiate objects
    prefs = AboutPrefs(driver, category="privacy")
    networking = AboutNetworking(driver)
    tabs = TabBar(driver)
    test_page = GenericPage(driver, url=TEST_URL)

    # Add the domain to the DoH exceptions list
    prefs.open()
    prefs.open_doh_exceptions_dialog()
    prefs.add_doh_exception(EXCEPTION_DOMAIN)

    # Reach the excepted website in a new tab
    tabs.open_and_switch_to_new_tab()
    test_page.open()

    # Verify the excepted host was resolved by the OS DNS resolver, not TRR
    networking.open()
    networking.select_network_category("dns")
    networking.wait_for_dns_entry(TEST_HOST, trr="false")
