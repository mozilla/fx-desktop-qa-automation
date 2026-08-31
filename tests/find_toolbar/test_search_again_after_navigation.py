import pytest
from selenium.webdriver import Firefox

from modules.browser_object import FindToolbar
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "127264"


TARGET_PAGE = (
    "https://firefox-source-docs.mozilla.org/devtools-user/browser_toolbox/index.html"
)
SEARCH_TERM = "browser"
MIN_MATCHES = 10  # the page had 25 matches when the test was written
NEXT_PAGE_URL_PART = "tools_toolbox"


@pytest.fixture()
def temp_selectors():
    return {
        "toolbox-link": {
            "selectorData": (
                "div[itemprop='articleBody'] a[href$='tools_toolbox/index.html']"
            ),
            "strategy": "css",
            "groups": [],
        },
    }


def test_search_again_after_navigation(
    driver: Firefox,
    find_toolbar: FindToolbar,
    current_match: str,
    temp_selectors: dict,
):
    """
    C127264: Verify that searching again after navigating to another page works

    Arguments:
        find_toolbar: instantiation of FindToolbar BOM.
        current_match: script returning info about the currently highlighted match.
        temp_selectors: the in-content link to the next page.
    """
    page = GenericPage(driver, url=TARGET_PAGE)
    page.elements |= temp_selectors
    page.open()

    # Search the term
    find_toolbar.open_with_key_combo()
    find_toolbar.find(SEARCH_TERM)
    find_toolbar.expect(lambda _: find_toolbar.get_match_args()["total"] >= MIN_MATCHES)

    # Follow a link, the findbar stays open with the term in it
    page.click_on("toolbox-link")
    page.url_contains(NEXT_PAGE_URL_PART)

    # Navigating drops the highlight
    page.expect_not(lambda d: d.execute_script(current_match))

    # Selecting the findbar and hitting ENTER searches the new page for the same term
    find_toolbar.click_on("find-toolbar-input")
    find_toolbar.fill("find-toolbar-input", "", clear_first=False)

    # The searched word is highlighted on the new page
    def search_term_highlighted(d):
        match = d.execute_script(current_match)
        return match and match[0].lower() == SEARCH_TERM

    page.expect(search_term_highlighted)
