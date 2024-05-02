import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation

sites = ["Google", "Amazon", "Bing", "DuckDuckGo", "eBay"]


@pytest.mark.parametrize("site", sites)
def test_search_engine_one_off_buttons(driver: Firefox, site: str):
    """
    Make sure the 'Next time, search with' buttons work for supported search engines
    """
    nav = Navigation(driver).open()
    nav.get_awesome_bar().click()
    nav.click_one_off_search_button(site)
    nav.assert_search_mode_matches(site)
