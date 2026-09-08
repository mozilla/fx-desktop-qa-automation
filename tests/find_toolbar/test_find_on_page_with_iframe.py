import json
from pathlib import Path
from shutil import copyfile

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import FindToolbar
from modules.page_object import GenericPage

PARENT_HTML = "find_in_iframe_page.html"
FRAME_HTML = "find_in_iframe_frame.html"
SEARCH_TERM = "language"
PARENT_MATCHES = 5  # in the parent document
FRAME_MATCHES = 3  # inside the iframe
TOTAL_MATCHES = PARENT_MATCHES + FRAME_MATCHES


@pytest.fixture()
def test_case():
    return "127265"


@pytest.fixture()
def temp_selectors():
    return {
        "content-iframe": {
            "strategy": "css",
            "selectorData": "iframe.frame",
            "groups": ["doNotCache"],
        }
    }


@pytest.fixture()
def local_doc_path(tmp_path: Path) -> str:
    """Copy the page and the page it frames into a temp folder"""
    for filename in (PARENT_HTML, FRAME_HTML):
        copyfile(f"data/pages/{filename}", tmp_path / filename)
    return f"file://{tmp_path / PARENT_HTML}"


@pytest.fixture()
def web_page(driver: Firefox, temp_selectors: dict, local_doc_path: str):
    """Return the opened local page that contains an iframe"""
    generic_page = GenericPage(driver, url=local_doc_path)
    generic_page.elements |= temp_selectors
    generic_page.open()
    yield generic_page


def _single_highlight(driver: Firefox, script: str) -> bool:
    """The current frame holds one highlight, and it is the search term"""
    match = driver.execute_script(script)
    # Match Case is off by default
    return bool(match) and match[0].lower() == SEARCH_TERM and match[1] == 1


def _no_highlight(driver: Firefox, script: str) -> bool:
    """The current frame holds no highlighted text"""
    match = driver.execute_script(script)
    return not match or not match[0].strip()


def _match_args(find_toolbar: FindToolbar) -> dict:
    """The findbar counter, empty while it has not been populated"""
    args = find_toolbar.get_element("matches-label").get_attribute("data-l10n-args")
    return json.loads(args) if args else {}


def test_find_on_page_with_iframe(
    driver: Firefox,
    find_toolbar: FindToolbar,
    web_page: GenericPage,
    current_match: str,
):
    """
    C127265: Verify that searching on a page with iframe works properly

    The checkerboarding and performance checks stay manual.

    Arguments:
        find_toolbar: instantiation of FindToolbar BOM.
        web_page: the local page that contains an iframe.
        current_match: script returning info about the currently highlighted match.
    """
    # All matches are found, parent and iframe
    find_toolbar.open_with_key_combo()
    find_toolbar.find(SEARCH_TERM)
    find_toolbar.expect(
        lambda _: _match_args(find_toolbar).get("total") == TOTAL_MATCHES
    )

    # First match is in the parent, and is the only highlight
    find_toolbar.rewind_to_first_match()
    web_page.expect(lambda d: _single_highlight(d, current_match))
    first_match = driver.execute_script(current_match)

    # F3 moves the highlight forward, SHIFT+F3 moves it back
    find_toolbar.navigate_matches_by_keys()
    web_page.expect(
        lambda d: d.execute_script(current_match) not in (None, first_match)
    )
    find_toolbar.navigate_matches_by_keys(backwards=True)
    web_page.expect(lambda d: d.execute_script(current_match) == first_match)

    # The last parent match still highlights in the parent
    find_toolbar.navigate_matches_n_times(PARENT_MATCHES - 1)
    find_toolbar.expect(
        lambda _: _match_args(find_toolbar).get("current") == PARENT_MATCHES
    )
    web_page.expect(lambda d: _single_highlight(d, current_match))

    # One more crosses into the iframe
    find_toolbar.next_match()
    find_toolbar.expect(
        lambda _: _match_args(find_toolbar).get("current") == PARENT_MATCHES + 1
    )
    web_page.expect(lambda d: _no_highlight(d, current_match))

    web_page.switch_to_iframe_context(web_page.get_element("content-iframe"))
    web_page.expect(lambda d: _single_highlight(d, current_match))
    web_page.switch_to_default_frame()

    # Going back brings it out of the iframe
    find_toolbar.previous_match()
    web_page.expect(lambda d: _single_highlight(d, current_match))
    last_parent_match = driver.execute_script(current_match)

    # Scrolling leaves the search session intact
    driver.execute_script("window.scrollBy(0, 2000)")
    driver.execute_script("window.scrollTo(0, 0)")
    web_page.expect(lambda d: d.execute_script(current_match) == last_parent_match)
    find_toolbar.expect(
        lambda _: _match_args(find_toolbar).get("total") == TOTAL_MATCHES
    )
