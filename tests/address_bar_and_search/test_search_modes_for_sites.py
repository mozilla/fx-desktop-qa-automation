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
    # search in bar the site
    nav = Navigation(driver).open()
    # mode is optional because it will try to enter it as the little shard if specified
    nav.search("soccer", mode=site)
    # verify its in the search bar
    nav.expect_in_content(EC.url_contains(site.lower()))
    # close
    nav.clear_awesome_bar()
