import pytest
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation
from modules.page_object_prefs import AboutPrefs
from modules.util import BrowserActions

GENERAL_ENGINE = "Bing"
QUERY = "cobra kai"


@pytest.fixture()
def test_case():
    return "3028715"


def test_search_mode_appears_and_suggestions_update(driver):
    """
    Steps:
      1) Open a new tab.
      2) Start typing in the address bar.
      3) Suggestions list starts to populate using the default search engine.
      4) Click the USB and select another search engine from the list.
      5) Search mode appears (left side). Check suggestions list.
      6) Search terms are retained and new suggestions are returned.
      7) Click one of the search suggestions.
      8) A search is done using the engine selected from step 4.
    """
    nav = Navigation(driver)
    actions = BrowserActions(driver)

    # 1) Open a new tab
    nav.open_and_switch_to_new_window("tab")

    # 2) Start typing (no Enter)
    actions.search(QUERY, with_enter=False)

    # 3) Suggestions list populates (default engine)
    nav.wait_for_suggestions_present()

    # 4) Click the USB and select another engine
    nav.open_usb_and_select_engine(GENERAL_ENGINE)

    # 5) Search mode chip appears
    nav.assert_search_mode_chip_visible()
    nav.wait_for_suggestions_present()

    # 6–7) Click a visible suggestion
    nav.click_first_suggestion_row()

    # 8) Verify search executed with selected engine
    nav.expect_in_content(EC.url_contains(GENERAL_ENGINE.lower()))
    nav.clear_awesome_bar()


def test_private_mode_repeat_after_enabling_pref(driver):
    """
      - Enable “Show search suggestions in Private Windows”.
      - Open Private Window.
      - Repeat steps 1–5 (verify search works with selected engine).
    """
    nav = Navigation(driver)
    actions = BrowserActions(driver)

    # Enable PBM suggestions pref by its known ID
    AboutPrefs(driver, category="search").open().enable_private_window_suggestions()

    # Open Private Window using BasePage method
    nav.open_and_switch_to_new_window("private")

    try:
        # Repeat steps 1–8 in Private Mode
        nav.open_and_switch_to_new_window("tab")
        actions.search(QUERY, with_enter=False)

        nav.wait_for_suggestions_present()
        nav.open_usb_and_select_engine(GENERAL_ENGINE)
        nav.assert_search_mode_chip_visible()
        nav.wait_for_suggestions_present()

        nav.click_first_suggestion_row()
        nav.expect_in_content(EC.url_contains(GENERAL_ENGINE.lower()))
        nav.clear_awesome_bar()
    finally:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
