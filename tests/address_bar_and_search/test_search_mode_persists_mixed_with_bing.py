import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "3028730"


@pytest.mark.parametrize("engine", ["DuckDuckGo"])
def test_search_mode_persists_mixed_with_bing(driver: Firefox, engine):
    """
    TC 3028730: Ensure '@bing' is NOT recognized as a special Bing search when DuckDuckGo is selected.
    """
    # Open a neutral page (new tab) and prepare helpers
    page = GenericPage(driver, url="about:newtab")
    nav = Navigation(driver)

    page.open()

    # Step 1: pick DuckDuckGo from the search mode switcher (aka USB)
    nav.click_search_mode_switcher()
    nav.set_search_mode(engine)

    # Step 2: type '@bing' in the Awesome Bar
    nav.click_in_awesome_bar()
    nav.type_in_awesome_bar("@bing")

    # Assert that the "tab to search" / alias UI is NOT shown for '@bing'
    nav.element_not_visible("tab-to-search-text-span")

    # Step 3: continue typing any word and hit Enter
    nav.type_in_awesome_bar(" test" + Keys.ENTER)

    # Expectation: a DuckDuckGo results page, with '@bing' included as plain text in the query.
    page.url_contains("duckduckgo.com")

    # Verify '@bing' appears in the query (allowing for URL encoding)
    current_url = driver.current_url
    assert ("%40bing" in current_url) or ("@bing" in current_url), (
        f"@bing should be part of the search term, but URL was: {current_url}"
    )
