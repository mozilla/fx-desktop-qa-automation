import pytest
from selenium.webdriver import Firefox, Keys
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation

# This list defines pairs of site names and their corresponding index in the UI.
# Each tuple corresponds to a different search engine button on the Awesome Bar.
sites = [("Google", 0), ("Amazon", 1), ("Bing", 2), ("DuckDuckGo", 3), ("eBay", 4)]

# Using pytest's parameterization to run the same test across multiple site-index pairs.
# This allows the test to be executed for each specified search engine.
@pytest.mark.parametrize("site, index", sites)
def test_click_modes_for_sites(driver: Firefox, site: str, index: int):
    """
    Tests clicking on search engine buttons in the Awesome Bar and performing a search.

    This test opens the navigation page, clicks the specified search engine button by its name
    and index, types a query into the Awesome Bar, checks if the resulting page's URL
    contains the search engine's name, and finally clears the Awesome Bar.

    Parameters:
        driver (Firefox): The Selenium WebDriver instance for Firefox.
        site (str): The name of the search engine to test.
        index (int): The index of the search engine button in the Awesome Bar.
    """

    # Initialize the Navigation page object and open the browser to the starting page.
    nav = Navigation(driver).open()

    # Click the search button for the specified site using its name and index.
    nav.click_on_onoff_search_button(site, index)

    # Type a search term into the Awesome Bar and initiate the search.
    nav.type_in_awesome_bar("soccer" + Keys.ENTER)

    # Expect the resulting URL to contain the search engine's name in a lower case.
    nav.expect_in_content(EC.url_contains(site.lower()))

    # Clear the text from the Awesome Bar to reset the state for potential further actions.
    nav.clear_awesome_bar()
