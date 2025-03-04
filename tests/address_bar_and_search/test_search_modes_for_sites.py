import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation


@pytest.fixture()
def test_case():
    return "2234690"


# Dictionary mapping search engines to their expected input prefix
search_modes = [
    ("Bing", "Bi", "https://www.bing.com"),
    ("DuckDuckGo", "Du", "https://duckduckgo.com"),
    ("Wikipedia", "Wi", "https://en.wikipedia.org"),
]


@pytest.mark.parametrize("site, prefix, url", search_modes)
def test_search_modes_for_sites(driver: Firefox, site, prefix, url):
    """C2234690: Test that search modes can be activated by typing the first two letters."""
    nav = Navigation(driver)
    driver.get(url)
    nav.open_and_switch_to_new_window("tab")

    # Type the first two letters into the Awesome Bar
    nav.type_in_awesome_bar(prefix)

    nav.type_in_awesome_bar(Keys.TAB)

    # Perform the search
    nav.type_in_awesome_bar("soccer" + Keys.ENTER)

    # Validate that the correct search engine is used
    nav.expect_in_content(EC.url_contains(site.lower()))
