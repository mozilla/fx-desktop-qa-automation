import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait

from modules.browser_object import Navigation, TabBar

SEARCH_SETTINGS_URL = "about:preferences#search"


@pytest.fixture()
def test_case():
    return "3897533"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.search.widget.new", True)]


def test_search_settings_opens_from_new_widget(driver: Firefox):
    """
    C3897533 - The about:preferences#search page can be accessed via the
    new search box widget.
    """
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Precondition: search bar enabled on the toolbar
    nav.add_search_bar_to_toolbar()

    # Open a new tab and focus the search box widget
    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    tabs.switch_to_new_tab()

    # Search Settings must not be open yet
    assert SEARCH_SETTINGS_URL not in driver.current_url

    # Note: despite the 'legacy' in the method name, this targets the new
    # search box widget introduced in Firefox 138+ (#searchbar-new). The
    # helper opens the widget dropdown, verifies the 'Search Settings' item
    # is present, and clicks it.
    num_tabs_before = len(driver.window_handles)
    nav.click_on_legacy_search_settings_button()

    nav.url_contains(SEARCH_SETTINGS_URL)
    assert len(driver.window_handles) == num_tabs_before, (
        "Search Settings opened in a new tab instead of the current one"
    )


def test_search_settings_focuses_existing_tab(driver: Firefox):
    """
    C3897533 - If about:preferences#search is already open, choosing
    'Search Settings' from the widget brings that tab into focus.
    """
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Precondition: search bar enabled on the toolbar
    nav.add_search_bar_to_toolbar()

    # First settings tab: open via the widget (matches the user flow)
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    nav.click_on_legacy_search_settings_button()
    nav.url_contains(SEARCH_SETTINGS_URL)

    # Another fresh tab so the settings tab goes to the background
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    num_tabs_before = len(driver.window_handles)

    # Trigger 'Search Settings' again. Same note as above applies to the
    # 'legacy' method name: it targets the new search box widget.
    nav.click_on_legacy_search_settings_button()

    # geckodriver does not follow Firefox-internal tab switches, so ask
    # the browser itself which tab is currently selected.
    nav.set_chrome_context()
    try:
        WebDriverWait(driver, 5).until(
            lambda d: SEARCH_SETTINGS_URL
            in d.execute_script("return gBrowser.selectedBrowser.currentURI.spec")
        )
    finally:
        nav.set_content_context()

    # No new tab was created; the existing settings tab got focus
    assert len(driver.window_handles) == num_tabs_before, (
        "A new tab was opened instead of focusing the existing one"
    )
