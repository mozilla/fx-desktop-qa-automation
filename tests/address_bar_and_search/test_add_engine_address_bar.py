import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation


@pytest.fixture()
def test_case():
    return "1365478"


sites = [("YouTube", "com"), ("Ecosia", "org")]


@pytest.mark.parametrize("site, domain", sites)
def test_add_search_engine_from_address_bar(driver: Firefox, site: str, domain: str):
    """
    C1365478: Test that an open search engine can be added from the address bar.
    """
    open_site_engine = site.lower()
    nav = Navigation(driver)

    # Construct the full URL
    full_url = f"https://www.{open_site_engine}.{domain}"

    # Search the URL and wait until is loaded
    nav.search(full_url)
    nav.custom_wait(timeout=20).until(EC.url_contains(full_url))

    with driver.context(driver.CONTEXT_CHROME):
        # Add the search engine
        nav.click_in_awesome_bar()
        nav.element_clickable("add-extra-search-engine", labels=[site])
        nav.click_on("add-extra-search-engine", labels=[site])

        # Select the new search engine
        nav.element_clickable("search-one-off-engine-button", labels=[site])
        nav.click_on("search-one-off-engine-button", labels=[site])

        # Search for a term to verify the added search engine is working
        nav.search("cobra")
        nav.expect_in_content(EC.url_contains(open_site_engine))
