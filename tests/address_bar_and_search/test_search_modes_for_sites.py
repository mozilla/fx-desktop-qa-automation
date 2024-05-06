import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation

sites = ["Google", "Amazon", "Bing", "DuckDuckGo", "eBay"]


@pytest.mark.parametrize("site", sites)
def test_search_modes_for_sites(driver: Firefox, site: str):
    """
    Test that the Awesome bar contains the site shard and search for arbitrary item

    Parameters
    ----------
    driver: WebDriver
        The instance of the webdriver (Firefox)

    sites: str[]
        The list of search options to try

    """
    nav = Navigation(driver).open()
    nav.search("soccer", mode=site)
    nav.expect_in_content(EC.url_contains(site.lower()))
    nav.clear_awesome_bar()
