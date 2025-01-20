import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation


@pytest.fixture()
def test_case():
    return "2567890"


@pytest.mark.parametrize(
    "search_mode",
    ["Google", "eBay", "Bing", "DuckDuckGo", "Wikipedia (en)", "Amazon.com"],
)
def test_search_engine_selector_and_validator(driver: Firefox, search_mode: str):
    """
    Select Appropriate search engine and go to site, asserting that the correct search engine was used.

    Parameters:
        driver (FireFox): webdriver used for communicating with the browser.
        search_mode (str): search parameter selected from the awesome bar.
    """
    nav = Navigation(driver)
    url_element_search_mode = search_mode.split()[0].lower()
    nav.click_search_mode_switcher()
    nav.set_search_mode(search_mode)
    nav.search("soccer")
    nav.expect_in_content(EC.url_contains(url_element_search_mode))
    assert url_element_search_mode in driver.current_url
    nav.clear_awesome_bar()
