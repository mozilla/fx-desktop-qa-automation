import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation


@pytest.fixture()
def test_case():
    return "2567892"


@pytest.mark.parametrize(
    "search_mode",
    ["Google", "Bing", "DuckDuckGo", "eBay"],
)
def test_search_mode_selector_and_validator_keyboard(driver: Firefox, search_mode: str):
    """
    Select Appropriate search mode and go to site, asserting that the correct search mode was used.
    Select search mode through keyboard.
    Parameters:
        driver (FireFox): webdriver used for communicating with the browser.
        search_mode (str): search parameter selected from the awesome bar.
    """
    nav = Navigation(driver)
    url_element_search_mode = search_mode.split()[0].lower()
    nav.search("soccer", mode=search_mode)
    # didn't use url_contains because it always hangs at the page even though the url should match the mode
    nav.expect_in_content(EC.url_contains(url_element_search_mode))
    assert url_element_search_mode in driver.current_url


@pytest.mark.parametrize(
    "search_mode",
    ["Google", "Bing", "DuckDuckGo", "eBay"],
)
def test_search_mode_selector_and_validator_mouse(driver: Firefox, search_mode: str):
    """
    Select Appropriate search mode and go to site, asserting that the correct search mode was used.
    Select search mode through mouse.
    Parameters:
        driver (FireFox): webdriver used for communicating with the browser.
        search_mode (str): search parameter selected from the awesome bar.
    """
    nav = Navigation(driver)
    url_element_search_mode = search_mode.split()[0].lower()
    # a bit hacky but prefered this over having the chrome context opened here for clicking on the awesome bar.
    nav.search("")
    nav.click_on(
        "search-one-off-engine-button",
        labels=[f"{search_mode} (@{url_element_search_mode})"],
    )
    nav.search("soccer")
    # didn't use url_contains because it always hangs at the page even though the url should match the mode
    nav.expect_in_content(EC.url_contains(url_element_search_mode))
    assert url_element_search_mode in driver.current_url
