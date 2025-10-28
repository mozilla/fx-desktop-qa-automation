import pytest
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from modules.browser_object import Navigation
from modules.page_object_prefs import AboutPrefs

RANDOM_TEXT = "cluj"
GLOBAL_SUGGESTIONS_CHECKBOX_ID = "showSearchSuggestionsFirstCheckbox"


def _type_in_urlbar_and_collect_titles(nav: Navigation, text: str) -> list:
    nav.clear_awesome_bar()
    nav.type_in_awesome_bar(text)
    return nav.get_elements("suggestion-titles")


def _try_type_in_searchbar_and_collect_titles(nav: Navigation, text: str) -> list | None:
    """Return list of titles if Search Bar exists, else None."""
    try:
        nav.set_search_bar()
    except NoSuchElementException:
        return None
    nav.type_in_search_bar(text)
    return nav.get_elements("suggestion-titles")


@pytest.mark.functional
def test_search_suggestions_pref_affects_urlbar_and_searchbar(driver):
    nav = Navigation(driver)

    prefs = AboutPrefs(driver, category="search").open()
    checkbox = driver.find_element(By.ID, GLOBAL_SUGGESTIONS_CHECKBOX_ID)

    # Ensure the checkbox is ENABLED before starting
    if checkbox.get_attribute("checked") != "true":
        checkbox.click()

    # --- Step 1: Disable the pref
    checkbox = driver.find_element(By.ID, GLOBAL_SUGGESTIONS_CHECKBOX_ID)
    if checkbox.get_attribute("checked") == "true":
        checkbox.click()

    try:
        # --- Step 2: Validate NO suggestions when disabled
        titles = _type_in_urlbar_and_collect_titles(nav, RANDOM_TEXT)
        assert len(titles) == 0, "Suggestions should be disabled for the Address Bar."

        titles_sb = _try_type_in_searchbar_and_collect_titles(nav, RANDOM_TEXT)
        if titles_sb is not None:
            assert len(titles_sb) == 0, "Suggestions should be disabled for the Search Bar."

    finally:
        # --- Step 3: Re-enable to restore original state
        prefs.open()
        checkbox = driver.find_element(By.ID, GLOBAL_SUGGESTIONS_CHECKBOX_ID)
        if checkbox.get_attribute("checked") != "true":
            checkbox.click()

    # --- Step 4: Validate that suggestions appear when enabled
    titles = _type_in_urlbar_and_collect_titles(nav, RANDOM_TEXT)
    assert len(titles) > 0, "Suggestions should be visible for the Address Bar when enabled."

    titles_sb = _try_type_in_searchbar_and_collect_titles(nav, RANDOM_TEXT)
    if titles_sb is not None:
        assert len(titles_sb) > 0, "Suggestions should be visible for the Search Bar when enabled."
