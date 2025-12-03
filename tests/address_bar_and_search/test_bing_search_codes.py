import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TabBar
from modules.page_object import AboutPrefs

SEARCH_ENGINE = "Bing"
SEARCH_TERM = "earth"
TAB_TITLE = f"{SEARCH_TERM} - Search"
BING_CODES = ["form=MOZLBR&pc=MOZI", "pc=MOZI&form=MOZLBR"]


@pytest.fixture()
def test_case():
    return "3029767"


def test_bing_search_codes(driver: Firefox):
    """
    C3029767 - Verify that Search Code Testing: Bing - US is correctly displayed and functional.
    """
    nav = Navigation(driver)
    prefs = AboutPrefs(driver)
    tab = TabBar(driver)

    # Go to search engine settings
    nav.open_searchmode_switcher_settings()

    # Change the default search engine
    prefs.search_engine_dropdown().select_option(SEARCH_ENGINE)

    # Open a tab and verify Bing search code
    driver.get("about:newtab")
    nav.search(SEARCH_TERM)
    tab.expect_title_contains(TAB_TITLE)
    assert any(code in driver.current_url for code in BING_CODES)
    nav.clear_awesome_bar()
