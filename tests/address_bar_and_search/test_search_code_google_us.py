from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import ContextMenu, Navigation, TabBar
from modules.page_object import AboutConfig

# Set constant
FX_SEARCH_CODE = "client=firefox-b-1-d"
SEARCH_BAR_PREF = "browser.search.widget.inNavBar"


def test_search_code_google_us(driver: Firefox):
    """
    C1365268 - Default Search Code: Google - US
    This tests multiple ways of sending a search; Awesome bar,
    Search bar and selected text
    """

    # Create objects
    nav = Navigation(driver).open()
    ac = AboutConfig(driver)
    context_menu = ContextMenu(driver)
    tab = TabBar(driver)

    def search_code_assert():
        # Function to check the search code of a Google search in US region
        nav.set_content_context()
        search_url = driver.current_url
        assert FX_SEARCH_CODE in search_url
        nav.clear_awesome_bar()

    # Check code generated from the Awesome bar search
    nav.search("soccer")
    nav.expect(EC.title_contains("Google Search"))
    search_code_assert()

    # Check code generated from the Search bar search
    # First enable search bar via about:config
    ac.toggle_true_false_config(SEARCH_BAR_PREF)
    nav.clear_awesome_bar()

    # Then run the code check
    nav.search_bar_search("soccer")
    tab.expect_title_contains("Google Search")
    search_code_assert()

    # Check code generated from the context click of selected text
    nav.set_content_context()
    driver.get("http://example.com")
    h1_tag = driver.find_element(By.TAG_NAME, "h1")
    nav.triple_click(h1_tag)
    nav.context_click_element(h1_tag)
    nav.set_chrome_context()
    context_menu.get_context_item("context-menu-search-selected-text").click()
    nav.hide_popup("contentAreaContextMenu")

    # Switch to the newly opened tab and run the code check
    window_handles = driver.window_handles
    driver.switch_to.window(window_handles[-1])
    tab.expect_title_contains("Google Search")
    search_code_assert()
