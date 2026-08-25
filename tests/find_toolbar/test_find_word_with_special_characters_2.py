import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait

from modules.browser_object import FindToolbar


@pytest.fixture()
def test_case():
    return "127276"


@pytest.fixture()
def add_to_prefs_list():
    """Make sure the site is served in Japanese"""
    return [("intl.accept_languages", "ja-JP, ja")]


TARGET_PAGE = "https://ja.wikipedia.org/wiki/辻希美"
SEARCH_TERM = "辻希美"
MIN_MATCHES = 30  # the page had 74 matches when the test was written

# Text, selected range count and DOM position of the current match, null while there is none
CURRENT_MATCH = """
    const selection = window.getSelection();
    if (!selection || !selection.rangeCount) return null;
    const range = selection.getRangeAt(0);
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node = -1;
    for (let i = 0; walker.nextNode(); i++) {
      if (walker.currentNode === range.startContainer) {
        node = i;
        break;
      }
    }
    return [selection.toString(), selection.rangeCount, node, range.startOffset];
"""


def test_find_word_with_special_characters_2(
    driver: Firefox, find_toolbar: FindToolbar
):
    """
    C127276: Verify that there are no issues when searching a word that contains
    special characters (2)

    Arguments:
        find_toolbar: instantiation of FindToolbar BOM.
    """
    driver.get(TARGET_PAGE)

    # Every match of a word with special characters is found
    find_toolbar.open_with_key_combo()
    find_toolbar.find(SEARCH_TERM)
    total_matches = find_toolbar.match_dict["total"]
    assert total_matches >= MIN_MATCHES

    # The searched word is the only highlight
    find_toolbar.rewind_to_first_match()
    first_match = WebDriverWait(driver, 10).until(
        lambda d: d.execute_script(CURRENT_MATCH)
    )
    # Match Case is off by default, so the match may differ in case from the search term
    assert first_match[0].lower() == SEARCH_TERM
    assert first_match[1] == 1

    # F3 moves the highlight forward, SHIFT+F3 moves it back
    find_toolbar.navigate_matches_by_keys()
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script(CURRENT_MATCH) not in (None, first_match)
    )
    find_toolbar.navigate_matches_by_keys(backwards=True)
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script(CURRENT_MATCH) == first_match
    )

    # Scrolling up and down leaves the search session intact
    driver.execute_script("window.scrollBy(0, 2000)")
    driver.execute_script("window.scrollTo(0, 0)")
    assert driver.execute_script(CURRENT_MATCH) == first_match
    assert find_toolbar.get_match_args()["total"] == total_matches
