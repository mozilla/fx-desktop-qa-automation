import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_prefs import AboutPrefs
from modules.util import BrowserActions

# Constants
SEARCH_TERM_SPONSORED = "iphone"
SEARCH_TERM_NON_SPONSORED = "wiki"
RETRY_LIMIT = 5


@pytest.fixture()
def test_case():
    return "3029158"


def test_search_suggests_enabled(driver: Firefox):
    """
    C1618400: Firefox Suggest displays sponsored and non-sponsored suggestions when enabled in Preferences
    """
    nav = Navigation(driver)
    prefs = AboutPrefs(driver, category="search")
    actions = BrowserActions(driver)

    prefs.open()

    # Enable "Show search suggestions" if disabled
    suggestions_checkbox = prefs.get_element("show-suggestions")
    if not suggestions_checkbox.is_selected():
        suggestions_checkbox.click()

    nonsponsored_checkbox = prefs.get_element("firefox-suggest-nonsponsored")
    assert nonsponsored_checkbox.is_selected(), (
        "'firefox-suggest-nonsponsored' checkbox not checked"
    )

    sponsored_checkbox = prefs.get_element("firefox-suggest-sponsored")
    assert sponsored_checkbox.is_selected(), (
        "'firefox-suggest-sponsored' checkbox not checked"
    )

    # Check for sponsored suggestion
    found_sponsored = False
    retries = 0
    while not found_sponsored and retries < RETRY_LIMIT:
        actions.search(SEARCH_TERM_SPONSORED, with_enter=False)
        with driver.context(driver.CONTEXT_CHROME):
            found_sponsored = any(
                item.get_attribute("aria-label") == "Sponsored"
                for item in nav.get_elements("sponsored-suggestion")
            )
        retries += 1
    assert found_sponsored, (
        f"No sponsored suggestion found after {RETRY_LIMIT} retries."
    )

    # Check for non-sponsored suggestion
    found_non_sponsored = False
    retries = 0
    while not found_non_sponsored and retries < RETRY_LIMIT:
        actions.search(SEARCH_TERM_NON_SPONSORED, with_enter=False)
        with driver.context(driver.CONTEXT_CHROME):
            try:
                nav.get_element("firefox-suggest")
                titles = nav.get_elements("suggestion-titles")
                found_non_sponsored = any("Wikipedia" in title.text for title in titles)
                break
            finally:
                retries = +1
                continue
    assert found_non_sponsored, (
        f"Non-sponsored suggestion not found after {RETRY_LIMIT} retries."
    )
