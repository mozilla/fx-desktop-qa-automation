import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import TabBar
from modules.page_object import AboutNetworking, AboutPrefs


@pytest.fixture()
def test_case():
    return "2300296"


@pytest.fixture()
def set_prefs():
    return [
        ("browser.search.region", "US"),
        ("doh-rollout.home-region", "US"),
        ("doh-rollout.mode", 2),
    ]


TEST_URL = "https://www.wikipedia.org/"


def test_doh_enforces_secure_dns_resolution(driver: Firefox):
    """
    C2300296 - Verify that default DNS over HTTPS (DoH) settings enforce secure DNS resolution
    """

    # Instantiate objects
    prefs = AboutPrefs(driver, category="privacy")
    networking = AboutNetworking(driver)
    tabs = TabBar(driver)

    # Confirm the default DoH settings
    prefs.open()
    prefs.element_has_text("doh-status", "Status: Active")
    prefs.element_has_text("doh-resolver", "Provider: Cloudflare")

    # Open the test site and subsequently the networking#dns page
    driver.get(TEST_URL)

    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    networking.open()
    networking.select_network_category("dns")

    # Check that the test site is resolved using TRR (true)
    rows = driver.find_elements(
        By.CSS_SELECTOR, "#dns_content tr"
    )  # Fetch all rows in the DNS table

    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if cells[0].text == "www.wikipedia.org":
            trr_status = cells[2].text  # Third column for TRR
            assert trr_status == "true"
            break
