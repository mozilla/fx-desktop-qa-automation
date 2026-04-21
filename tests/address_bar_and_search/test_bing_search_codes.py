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


@pytest.fixture()
def added_selectors():
    return {
        "default-engine-dropdown": {
            "selectorData": "defaultEngineNormal",
            "strategy": "id",
            "groups": [],
        },
        "shadow-panel-list": {
            "selectorData": ".content-wrapper panel-list",
            "strategy": "css",
            "shadowParent": "default-engine-dropdown",
            "groups": [],
        },
        "select-wrapper-button": {
            "selectorData": ".select-wrapper button",
            "strategy": "css",
            "shadowParent": "default-engine-dropdown",
            "groups": [],
        },
        "dropdown-item": {
            "selectorData": ".list slot panel-item",
            "strategy": "css",
            "shadowParent": "shadow-panel-list",
            "groups": [],
        },
        "dropdown-item2": {
            "selectorData": "panel-item[role='presentation']",
            "strategy": "css",
            "groups": [],
        },
    }


def test_bing_search_codes(driver: Firefox, added_selectors: dict):
    """
    C3029767 - Verify that Search Code Testing: Bing - US is correctly displayed and functional.
    """
    nav = Navigation(driver)
    prefs = AboutPrefs(driver, category="search")
    tab = TabBar(driver)
    prefs.elements |= added_selectors

    # Go to search engine settings
    nav.open_searchmode_switcher_settings()

    # Set Bing as default search engine
    prefs.select_default_search_engine_by_key(SEARCH_ENGINE)

    # Open a tab and verify Bing search code
    driver.get("about:newtab")
    nav.search(SEARCH_TERM)
    tab.expect_title_contains(TAB_TITLE)
    assert any(code in driver.current_url for code in BING_CODES)
    nav.clear_awesome_bar()
