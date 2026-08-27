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
MIN_MATCHES = 10  # the page had 25 matches when the test was written
TOOLBOX_LINK = (
    By.CSS_SELECTOR,
    "div[itemprop='articleBody'] a[href$='tools_toolbox/index.html']",
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

    # Search the term
    find_toolbar.open_with_key_combo()
    find_toolbar.find(SEARCH_TERM)
    assert find_toolbar.match_dict["total"] >= MIN_MATCHES

    # Follow a link, the findbar stays open with the term in it
    driver.find_element(*TOOLBOX_LINK).click()
    WebDriverWait(driver, 30).until(lambda d: "tools_toolbox" in d.current_url)

    # Navigating drops the highlight, hitting ENTER searches the new page
    assert driver.execute_script(current_match) is None
    with driver.context(driver.CONTEXT_CHROME):
        find_bar = find_toolbar.get_element("find-toolbar-input")
        find_bar.click()
        find_bar.send_keys(Keys.ENTER)

    # The searched word is the only highlight
    new_match = WebDriverWait(driver, 10).until(
        lambda d: d.execute_script(current_match)
    )
    assert new_match[0].lower() == SEARCH_TERM
