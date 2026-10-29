import pytest
from auto_fxui.browser_object import Navigation, TabBar
from auto_fxui.page_object import GenericPage
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

FIRST_URL = "cnn.com"
SECOND_URL = "mozilla.org"
DOMAIN_NAME = "facebook"
SEARCH_ENGINE = "DuckDuckGo"


@pytest.fixture()
def test_case():
    return "3897578"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.search.widget.new", True)]


def test_new_search_box_no_url_navigation(driver: Firefox):
    """
    C3897578 - The new search box widget doesn't allow URL navigation.
    """
    nav = Navigation(driver)
    tabs = TabBar(driver)
    page = GenericPage(driver)

    # Setup: add the search bar to the toolbar.
    nav.add_search_bar_via_customizable_ui()

    # Step 1: Enter a URL and press Enter; a SERP opens, not the site.
    tabs.open_and_switch_to_new_tab()
    nav.type_in_search_bar(FIRST_URL + Keys.ENTER)
    nav.url_contains(f"q={FIRST_URL}")

    # Step 2: Pick an engine, enter another URL and press Enter.
    # The search box keeps old text, so clear it first.
    tabs.open_and_switch_to_new_tab()
    nav.click_on("legacy-searchmode-switcher")
    nav.element_clickable("search-mode-switcher-option", labels=[SEARCH_ENGINE])
    nav.js_click_on("search-mode-switcher-option", labels=[SEARCH_ENGINE])
    nav.element_attribute_is(
        "legacy-searchmode-switcher-title", "textContent", SEARCH_ENGINE
    )
    nav.clear_search_bar()
    nav.type_in_search_bar(SECOND_URL + Keys.ENTER)
    nav.url_contains("duckduckgo.com")
    nav.url_contains(f"q={SECOND_URL}")

    # Step 3: Type a domain name and press Ctrl/Cmd + Enter; no .com is added.
    tabs.open_and_switch_to_new_tab()
    nav.clear_search_bar()
    nav.type_in_search_bar(DOMAIN_NAME)
    nav.perform_key_combo_chrome(Keys.CONTROL, Keys.ENTER)
    nav.url_contains(f"q={DOMAIN_NAME}")
    page.expect_not(EC.url_contains(f"{DOMAIN_NAME}.com"))
