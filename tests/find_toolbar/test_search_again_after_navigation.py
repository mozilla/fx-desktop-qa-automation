import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from modules.browser_object import FindToolbar


@pytest.fixture()
def test_case():
    return "127264"


TARGET_PAGE = (
    "https://firefox-source-docs.mozilla.org/devtools-user/browser_toolbox/index.html"
)
SEARCH_TERM = "browser"
TOOLBOX_LINK = (
    By.CSS_SELECTOR,
    "div[itemprop='articleBody'] a[href$='tools_toolbox/index.html']",
)
# innerText holds the same text the findbar searches, Match Case is off by default
COUNT_MATCHES = (
    f'return document.body.innerText.toLowerCase().split("{SEARCH_TERM}").length - 1'
)


def test_search_again_after_navigation(
    driver: Firefox, find_toolbar: FindToolbar, current_match: str
):
    """
    C127264: Verify that searching again after navigating to another page works

    Arguments:
        find_toolbar: instantiation of FindToolbar BOM.
        current_match: script returning info about the currently highlighted match.
    """
    driver.get(TARGET_PAGE)
    matches_on_first_page = driver.execute_script(COUNT_MATCHES)
    assert matches_on_first_page > 0

    # Search the term
    find_toolbar.open_with_key_combo()
    find_toolbar.find(SEARCH_TERM)
    assert find_toolbar.match_dict["total"] == matches_on_first_page

    # Follow a link, the findbar stays open with the term in it
    WebDriverWait(driver, 10).until(lambda d: d.find_element(*TOOLBOX_LINK)).click()
    WebDriverWait(driver, 30).until(lambda d: "tools_toolbox" in d.current_url)
    matches_on_new_page = driver.execute_script(COUNT_MATCHES)
    assert matches_on_new_page > 0

    # Hit ENTER again, the counter holds the old value for a moment
    with driver.context(driver.CONTEXT_CHROME):
        find_bar = find_toolbar.get_element("find-toolbar-input")
        find_bar.click()
        find_bar.send_keys(Keys.ENTER)
    WebDriverWait(driver, 10).until(
        lambda _: find_toolbar.get_match_args()["total"] == matches_on_new_page,
        message=f"Findbar never counted {matches_on_new_page} matches",
    )

    # The word is the only highlight
    new_match = driver.execute_script(current_match)
    assert new_match is not None
    assert new_match[0].lower() == SEARCH_TERM
    assert new_match[1] == 1
