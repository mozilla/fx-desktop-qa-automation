import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait

from modules.browser_object import FindToolbar


@pytest.fixture()
def test_case():
    return "127251"


@pytest.fixture()
def add_to_prefs_list():
    """Make sure the site is served in Arabic"""
    return [("intl.accept_languages", "ar")]


TARGET_PAGE = "https://ar.wikipedia.org/wiki/موزيلا_فايرفوكس"
SEARCH_TERM = "الش"
EXTRA_CHARS = "ركة"
MIN_MATCHES = 5  # the page had 13 matches when the test was written


def test_find_on_page_with_rtl_language(
    driver: Firefox, find_toolbar: FindToolbar, current_match: str
):
    """
    C127251: Verify that searching on a page with RTL language works properly

    Arguments:
        find_toolbar: instantiation of FindToolbar BOM.
        current_match: script returning info about the currently highlighted match.
    """
    driver.get(TARGET_PAGE)
    find_toolbar.open_with_key_combo()

    # Typing RTL characters into the find bar works
    find_toolbar.type_in_find_bar(SEARCH_TERM + EXTRA_CHARS)
    assert (
        find_toolbar.get_attribute_value("find-toolbar-input", "value")
        == SEARCH_TERM + EXTRA_CHARS
    )

    # Deleting them works too
    find_toolbar.delete_chars_from_find_bar(len(EXTRA_CHARS))
    assert (
        find_toolbar.get_attribute_value("find-toolbar-input", "value") == SEARCH_TERM
    )

    # Every match of the RTL search term is found
    find_toolbar.find(SEARCH_TERM)
    total_matches = find_toolbar.match_dict["total"]
    assert total_matches >= MIN_MATCHES

    # The searched text is the only highlight.
    # Selenium cannot read the find highlight, so current_match runs JS returning the
    # page selection as [text, range count, text node index, offset].
    find_toolbar.rewind_to_first_match()
    first_match = WebDriverWait(driver, 10).until(
        lambda d: d.execute_script(current_match)
    )
    assert first_match[0] == SEARCH_TERM
    assert first_match[1] == 1

    # F3 moves the highlight forward, SHIFT+F3 moves it back.
    # Re-running current_match shows which match the selection sits on now.
    find_toolbar.navigate_matches_by_keys()
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script(current_match) not in (None, first_match)
    )
    find_toolbar.navigate_matches_by_keys(backwards=True)
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script(current_match) == first_match
    )

    # Scrolling up and down leaves the search session intact.
    # These scripts scroll the page down 2000px, then back to the top.
    driver.execute_script("window.scrollBy(0, 2000)")
    driver.execute_script("window.scrollTo(0, 0)")
    # current_match again: the scroll should not have moved the selection
    assert driver.execute_script(current_match) == first_match
    assert find_toolbar.get_match_args()["total"] == total_matches
