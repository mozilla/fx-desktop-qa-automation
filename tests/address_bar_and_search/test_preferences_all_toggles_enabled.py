import pytest
from time import sleep
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_prefs import AboutPrefs
from modules.util import BrowserActions

# Constants
SEARCH_TERM_SPONSORED = "iphone"
SEARCH_TERM_NON_SPONSORED = "wiki"
RETRY_LIMIT = 20
SLEEP_BETWEEN_RETRIES = 3


@pytest.fixture()
def test_case():
    return "1618400"


def test_preferences_all_toggles_enabled(driver: Firefox):
    """
    C1618400: Preferences - All toggles buttons Enabled
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
        f"'firefox-suggest-nonsponsored' checkbox not checked"
    )

    sponsored_checkbox = prefs.get_element("firefox-suggest-sponsored")
    assert sponsored_checkbox.is_selected(), (
        f"'firefox-suggest-sponsored' checkbox not checked"
    )

    # Check for sponsored suggestion
    found_sponsored = False
    for _ in range(RETRY_LIMIT):
        actions.search(SEARCH_TERM_SPONSORED, with_enter=False)
        with driver.context(driver.CONTEXT_CHROME):
            sponsored_elements = nav.get_elements("sponsored-suggestion")
            found_sponsored = any(
                el.get_attribute("innerText") == "Sponsored"
                for el in sponsored_elements
            )
        if found_sponsored:
            break
        sleep(SLEEP_BETWEEN_RETRIES)

    assert found_sponsored, f"No sponsored suggestion found after {RETRY_LIMIT} retries."

    # Check for non-sponsored suggestion
    actions.search(SEARCH_TERM_NON_SPONSORED, with_enter=False)
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("firefox-suggest")
        nav.get_element("sponsored-suggestion")
        assert not any(
            el.get_attribute("innerText") == "Sponsored"
            for el in nav.get_elements("sponsored-suggestion")
        ), "Sponsored suggestion found when not expected."
