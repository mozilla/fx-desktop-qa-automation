import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TabBar
from modules.page_object import AboutConfig


# Set search region
@pytest.fixture()
def add_prefs():
    return [
        ("browser.urlbar.showSearchTerms.enabled", True),
        ("browser.urlbar.showSearchTerms.featureGate", True),
    ]


# Set constants
FIRST_SEARCH = "cheetah"
FIRST_RESULT = "https://www.google.com/search?client=firefox-b-1-d&q=cheetah"
SECOND_SEARCH = "lion"
SECOND_RESULT = "https://www.google.com/search?client=firefox-b-1-d&q=lion"
SEARCH_BAR_PREF = "browser.search.widget.inNavBar"


def test_search_term_persists(driver: Firefox):
    """
    C2153943 - Persist search term basic functionality
    """

    # Create objects
    nav = Navigation(driver).open()
    tab = TabBar(driver)

    def toggle_legacy_search_bar():
        # This test requires that the old search bar is added while retaining search results.
        # First, open a new tab and switch to it
        tab.new_tab_by_button()
        window_handles = driver.window_handles
        driver.switch_to.window(window_handles[-1])
        # Then, toggle the old search bar via about:config
        ac = AboutConfig(driver)
        ac.toggle_true_false_config(SEARCH_BAR_PREF)
        # Finally, close the about:config tab and switch context back to the original tab
        nav.set_chrome_context()
        x_icon = tab.get_element("tab-x-icon", multiple=True)
        x_icon[1].click()
        driver.switch_to.window(window_handles[0])

    # Perform a search using the URL bar.
    nav.search(FIRST_SEARCH)
    tab.expect_title_contains("Google Search")
    address_bar_text = nav.get_awesome_bar_text()
    assert FIRST_SEARCH == address_bar_text

    # Add the search bar to toolbar
    toggle_legacy_search_bar()

    # Search term should be replaced with full url
    address_bar_text = nav.get_awesome_bar_text()
    assert FIRST_RESULT == address_bar_text
    nav.clear_awesome_bar()

    # Perform a new awesome bar search, full url should be present
    # First, navigate away from Google
    nav.set_content_context()
    driver.get("about:robots")
    # Then perform another search
    nav.search(SECOND_SEARCH)
    tab.expect_title_contains("Google Search")
    address_bar_text = nav.get_awesome_bar_text()
    assert SECOND_RESULT == address_bar_text

    # Disable the old search bar
    toggle_legacy_search_bar()

    # Again, perform a search using the URL bar.
    nav.search(FIRST_SEARCH)
    tab.expect_title_contains("Google Search")
    address_bar_text = nav.get_awesome_bar_text()
    assert FIRST_SEARCH == address_bar_text
