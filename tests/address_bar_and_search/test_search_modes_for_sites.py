import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation

SEARCH_MODES = [
    ("Bing", "Bi", "https://www.bing.com"),
    ("DuckDuckGo", "Du", "https://duckduckgo.com"),
    ("Wikipedia", "Wi", "https://en.wikipedia.org"),
]


@pytest.fixture()
def test_case():
    return "3028754"


@pytest.mark.unstable(reason="Google re-captcha and manual tagged this test as removed")
@pytest.mark.parametrize("search_engine, prefix, url", SEARCH_MODES)
def test_search_modes_for_sites(
    driver: Firefox, search_engine: str, prefix: str, url: str
):
    """
    C2234690 - Verify that typing the first two letters of a search engine activates its mode in the address bar.
    """
    nav = Navigation(driver)
    driver.get(url)
    nav.open_and_switch_to_new_window("tab")

    nav.type_in_awesome_bar(prefix)
    nav.type_in_awesome_bar(Keys.TAB)
    nav.type_in_awesome_bar("soccer" + Keys.ENTER)

    nav.expect_in_content(EC.url_contains(search_engine.lower()))
