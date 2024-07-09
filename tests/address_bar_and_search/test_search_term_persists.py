import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TabBar
from modules.page_object import AboutConfig


# Set search region
@pytest.fixture()
def add_prefs():
    return [
        ("browser.search.region", "US"),
        ("browser.urlbar.showSearchTerms.enabled", True),
        ("browser.urlbar.showSearchTerms.featureGate", True),
    ]


# Set constants
FIRST_SEARCH = "cheetah"
FIRST_RESULT = "https://www.google.com/search?client=firefox-b-1-d&q=cheetah"
SECOND_SEARCH = "lion"
SECOND_RESULT = "https://www.google.com/search?client=firefox-b-1-d&q=lion"


def test_search_term_persists(driver: Firefox):
    """
    C2153943 - Persist search term basic functionality
    """

    # Create objects
    nav = Navigation(driver).open()
    tab = TabBar(driver)

    def toggle_old_search_bar():
        tab.new_tab_by_button()
        window_handles = driver.window_handles
        driver.switch_to.window(window_handles[-1])
        ac = AboutConfig(driver)
        pref = "browser.search.widget.inNavBar"
        ac.toggle_true_false_config(pref)
        nav.set_chrome_context()
        x_icon = tab.get_element("tab-x-icon", multiple=True)
        x_icon[1].click()
        driver.switch_to.window(window_handles[0])

    # Perform a search using the URL bar.
    nav.search(FIRST_SEARCH)
    tab.expect_title_contains("Google Search")
    nav.set_chrome_context()
    address_bar_text = nav.get_element("awesome-bar").get_attribute("value")
    assert FIRST_SEARCH == address_bar_text

    # Add the search bar to toolbar
    toggle_old_search_bar()

    # Search term should be replaced with full url
    address_bar_text = nav.get_element("awesome-bar").get_attribute("value")
    assert FIRST_RESULT == address_bar_text
    nav.clear_awesome_bar()

    # Perform a new awesome bar search, full url should be present
    # First, navigate away from Google
    nav.set_content_context()
    driver.get("about:robots")
    # Then perform another search
    nav.search(SECOND_SEARCH)
    tab.expect_title_contains("Google Search")
    nav.set_chrome_context()
    address_bar_text = nav.get_element("awesome-bar").get_attribute("value")
    assert SECOND_RESULT == address_bar_text

    # Disable the old search bar
    toggle_old_search_bar()

    # Again, perform a search using the URL bar.
    nav.search(FIRST_SEARCH)
    tab.expect_title_contains("Google Search")
    nav.set_chrome_context()
    address_bar_text = nav.get_element("awesome-bar").get_attribute("value")
    assert FIRST_SEARCH == address_bar_text
