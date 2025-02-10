import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation


@pytest.fixture()
def test_case():
    return "2234690"


# Dictionary mapping search engines to their expected input prefix
search_modes = {
    # "Google": "Go", No longer testing Google if this is the default search engine, due to Scotch Bonnet changes
    "Amazon": "Am",
    "Bing": "Bi",
    "DuckDuckGo": "Du",
    "eBay": "Eb",
}


@pytest.mark.parametrize("site, prefix", search_modes.items())
def test_search_modes_for_sites(driver: Firefox, site: str, prefix: str):
    """C2234690: Test that search modes can be activated by typing the first two letters."""
    nav = Navigation(driver)

    # Type the first two letters into the Awesome Bar
    nav.type_in_awesome_bar(prefix)

    nav.click_on("contextual_search_button_awesome_bar")

    # Perform the search
    nav.type_in_awesome_bar("soccer" + Keys.ENTER)

    # Validate that the correct search engine is used
    nav.expect_in_content(EC.url_contains(site.lower()))
    nav.clear_awesome_bar()
