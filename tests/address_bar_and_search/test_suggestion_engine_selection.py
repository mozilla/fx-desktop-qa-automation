import pytest
from selenium.webdriver import Firefox, Keys
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation

sites = ["Google", "Amazon.com", "Bing", "DuckDuckGo", "eBay"]


@pytest.mark.parametrize("site", sites)
def test_search_suggestion_for_engine_selection(driver: Firefox, site: str):
    """
    C1365228 - Test to verify that when entering "@", a list of search engines is suggested, and upon selecting an
    engine, the search is performed using the selected engine.
    """
    nav = Navigation(driver).open()
    nav.type_in_awesome_bar("@")

    # Use base selector to find all search engine suggestions
    suggestion_list_items = nav.get_element("search-suggestion-list", multiple=True)

    # Filter elements to find the one that matches the desired site
    suggestion_list_item = next(
        (item for item in suggestion_list_items if site in item.text), None
    )

    if suggestion_list_item:
        suggestion_list_item.click()
        nav.type_in_awesome_bar("soccer" + Keys.ENTER)
        nav.expect_in_content(EC.url_contains(site.lower()))
    else:
        pytest.fail(f"No search suggestion found for site: {site}")

    nav.clear_awesome_bar()
