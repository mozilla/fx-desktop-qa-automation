import pytest
from selenium.webdriver import Firefox

from modules.browser_object_context_menu import ContextMenu
from modules.browser_object_navigation import Navigation
from modules.page_object_newtab import AboutNewtab
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3029320"


@pytest.fixture()
def add_to_prefs_list():
    # Required to expose "Visit from clipboard" suggestions
    return [("browser.urlbar.clipboard.featureGate", True)]


TOPSITE_TITLE = "Wikipedia"


def test_clipboard_pref_flip(driver: Firefox):
    """
    3029320 – Verify clipboard suggestion appears in the URL bar
    after copying a TopSite link.
    """

    nav = Navigation(driver)
    context_menu = ContextMenu(driver)
    newtab = AboutNewtab(driver)
    prefs = AboutPrefs(driver)

    # Step 1: Open about:newtab
    driver.get("about:newtab")

    # Step 2: Copy a TopSite link via context menu
    topsite_el = newtab.get_topsite_element(TOPSITE_TITLE)

    newtab.hover(topsite_el)
    nav.verify_status_panel_url(TOPSITE_TITLE.lower())
    copied_url = nav.get_status_panel_url()

    newtab.open_topsite_context_menu_by_title(TOPSITE_TITLE)
    context_menu.click_context_item("context-menu-copy-link")

    # Step 3: Activate the Awesome Bar
    nav.clear_awesome_bar()
    nav.click_on("awesome-bar")

    # Step 4: Wait for clipboard suggestion (CHROME context)
    nav.click_on_clipboard_suggestion()

    # Step 5: Validate navigation & URL bar text
    nav.url_contains(copied_url)
    assert copied_url in nav.get_awesome_bar_text()

    # Step 6: Go to about:preferences#search and check the pref is enabled
    driver.get("about:preferences#search")
    prefs.verify_clipboard_suggestion_enabled()
