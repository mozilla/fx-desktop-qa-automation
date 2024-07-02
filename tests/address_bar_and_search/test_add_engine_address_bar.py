import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import Navigation

sites = [("YouTube", "com"), ("Ecosia", "org")]


# Set search region
@pytest.fixture()
def add_prefs():
    return [
        ("browser.search.region", "US"),
    ]


@pytest.mark.unstable
@pytest.mark.parametrize("site, domain", sites)
def test_add_search_engine_from_address_bar(driver: Firefox, site: str, domain: str):
    """
    C1365478: Test that an open search engine can be added from the address bar.
    """
    open_site_engine = site.lower()
    nav = Navigation(driver).open()

    # Construct the full URL
    full_url = f"https://www.{open_site_engine}.{domain}"
    nav.search(full_url)

    # Wait until the expected URL is loaded
    WebDriverWait(driver, 10).until(EC.url_contains(full_url))
    nav.click_in_awesome_bar()
    nav.element_clickable("add-extra-search-engine", labels=[site])
    nav.get_element("add-extra-search-engine", labels=[site]).click()
    nav.get_element("search-one-off-engine-button", labels=[site]).click()
    nav.search("cobra")
    nav.expect_in_content(EC.url_contains(open_site_engine))
