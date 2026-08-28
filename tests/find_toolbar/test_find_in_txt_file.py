import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait

from modules.browser_object import FindToolbar


@pytest.fixture()
def test_case():
    return "127273"


@pytest.fixture()
def add_to_prefs_list():
    """Enlarge plain text so the short .txt file is long enough to scroll"""
    return [("font.size.monospace.x-western", 48)]


TARGET_PAGE = "https://example-files.online-convert.com/document/txt/example.txt"
SEARCH_TERM = "Doe"
MIN_MATCHES = 15  # the file had 23 matches when the test was written


def test_find_in_txt_file(
    driver: Firefox, find_toolbar: FindToolbar, current_match: str
):
    """
    C127273: Verify that searching on a text file (.txt) works properly

    Arguments:
        find_toolbar: instantiation of FindToolbar BOM.
        current_match: script returning info about the currently highlighted match.
    """
    driver.get(TARGET_PAGE)

    # Every match in the plain text file is found
    find_toolbar.open_with_key_combo()
    find_toolbar.find(SEARCH_TERM)
    total_matches = find_toolbar.match_dict["total"]
    assert total_matches >= MIN_MATCHES

    # The first match is the only highlight
    find_toolbar.rewind_to_first_match()
    first_match = WebDriverWait(driver, 10).until(
        lambda d: d.execute_script(current_match)
    )
    # Match Case is off by default, so the match may differ in case from the search term
    assert first_match[0].lower() == SEARCH_TERM.lower()
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
    assert driver.execute_script(
        "return document.documentElement.scrollHeight > window.innerHeight"
    )
    driver.execute_script("window.scrollBy(0, 2000)")
    driver.execute_script("window.scrollTo(0, 0)")
    assert driver.execute_script(current_match) == first_match
    assert find_toolbar.get_match_args()["total"] == total_matches
