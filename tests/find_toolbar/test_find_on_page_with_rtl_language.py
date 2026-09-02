import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
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

    # Typing and deleting RTL characters works
    with driver.context(driver.CONTEXT_CHROME):
        find_input = find_toolbar.get_element("find-toolbar-input")
        find_input.send_keys(SEARCH_TERM + EXTRA_CHARS)
        assert find_input.get_property("value") == SEARCH_TERM + EXTRA_CHARS
        find_input.send_keys(Keys.BACK_SPACE * len(EXTRA_CHARS))
        assert find_input.get_property("value") == SEARCH_TERM

    # Every match of the RTL search term is found
    find_toolbar.find(SEARCH_TERM)
    total_matches = find_toolbar.match_dict["total"]
    assert total_matches >= MIN_MATCHES

    # The searched text is the only highlight
    find_toolbar.rewind_to_first_match()
    first_match = WebDriverWait(driver, 10).until(
        lambda d: d.execute_script(current_match)
    )
    assert first_match[0] == SEARCH_TERM
    assert first_match[1] == 1

    # F3 moves the highlight forward, SHIFT+F3 moves it back
    find_toolbar.navigate_matches_by_keys()
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script(current_match) not in (None, first_match)
    )
    find_toolbar.navigate_matches_by_keys(backwards=True)
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script(current_match) == first_match
    )

    # Scrolling up and down leaves the search session intact
    driver.execute_script("window.scrollBy(0, 2000)")
    driver.execute_script("window.scrollTo(0, 0)")
    assert driver.execute_script(current_match) == first_match
    assert find_toolbar.get_match_args()["total"] == total_matches
