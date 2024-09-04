import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation


@pytest.fixture()
def test_case():
    return "2234690"


sites = ["Google", "Amazon", "Bing", "DuckDuckGo", "eBay"]


@pytest.mark.ci
@pytest.mark.parametrize("site", sites)
def test_search_modes_for_sites(driver: Firefox, site: str):
    """C2234690: Test that search modes can be activated. May also cover C1365213 eventually"""
    nav = Navigation(driver).open()
    nav.search("soccer", mode=site)
    nav.expect_in_content(EC.url_contains(site.lower()))
    nav.clear_awesome_bar()
