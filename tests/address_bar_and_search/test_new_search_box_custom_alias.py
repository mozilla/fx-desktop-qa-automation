import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation, TabBar
from modules.page_object import AboutPrefs

DEFAULT_ENGINE = "Google"
ENGINE = "Bing"
ENGINE_ID = "bing"
ENGINE_DOMAIN = "bing.com"
ALIAS = "bang"
FIRST_TERM = "mozilla"
SECOND_TERM = "firefox"


@pytest.fixture()
def test_case():
    return "3897549"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.search.widget.new", True),
        ("browser.settings-redesign.enabled", True),
    ]


def test_new_search_box_custom_alias(driver: Firefox):
    """C3897549 - Custom set aliases work as expected in the new search box."""
    nav = Navigation(driver)
    tabs = TabBar(driver)
    prefs = AboutPrefs(driver, category="search")

    # Setup: add the search bar to the toolbar.
    nav.add_search_bar_via_customizable_ui()

    # Step 1: Open a new tab and go to about:preferences#search.
    tabs.open_and_switch_to_new_tab()
    prefs.open()

    # Step 2: Add the alias to Bing.
    prefs.edit_search_engine_keyword(ENGINE_ID, ALIAS)
    prefs.element_attribute_contains(
        "search-shortcuts-engine-row", "description", ALIAS, labels=[ENGINE]
    )

    # Step 3: Type @alias and press Enter to enter Bing search mode.
    nav.type_in_search_bar(f"@{ALIAS}")
    nav.perform_key_combo_chrome(Keys.ENTER)
    nav.element_attribute_contains(
        "legacy-searchmode-switcher-button", "aria-label", ENGINE
    )

    # Step 4: Search a string with Bing.
    nav.perform_key_combo_chrome(FIRST_TERM)
    nav.perform_key_combo_chrome(Keys.ENTER)
    nav.url_contains(ENGINE_DOMAIN)
    nav.url_contains(FIRST_TERM)

    # Step 5: Type the alias and a string, then press Enter.
    # Clear the box and leave Bing search mode first, so the alias is what picks Bing.
    nav.clear_search_bar()
    nav.type_in_search_bar(Keys.BACKSPACE)
    nav.element_attribute_contains(
        "legacy-searchmode-switcher-button", "aria-label", DEFAULT_ENGINE
    )
    nav.type_in_search_bar(f"{ALIAS} {SECOND_TERM}")
    nav.perform_key_combo_chrome(Keys.ENTER)
    nav.url_contains(ENGINE_DOMAIN)
    nav.url_contains(SECOND_TERM)
