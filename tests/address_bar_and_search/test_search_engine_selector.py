import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation

SEARCH_TERM = "soccer"
SEARCH_ENGINES = ["Google", "Amazon.com", "Bing", "DuckDuckGo", "eBay", "Wikipedia (en)"]


@pytest.fixture()
def test_case():
    return "1365151"


@pytest.mark.parametrize("search_engine", SEARCH_ENGINES)
def test_search_engine_selector_and_validator(driver: Firefox, search_engine: str):
    """
    C1365151 - Select appropriate search engine from the Awesomebar and verify the correct engine is used.
    """
    nav = Navigation(driver)

    expected_url_fragment = search_engine.split()[0].lower()
    nav.click_search_mode_switcher()
    nav.set_search_mode(search_engine)

    nav.search(SEARCH_TERM)
    nav.expect_in_content(lambda d: expected_url_fragment in d.current_url)


    assert expected_url_fragment in driver.current_url
    nav.clear_awesome_bar()
