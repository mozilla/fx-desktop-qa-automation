import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_sidebar import Sidebar
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutAddons


@pytest.fixture()
def test_case():
    return "2652535"


TREE_STYLE_TAB_URL = "https://addons.mozilla.org/en-US/firefox/addon/tree-style-tab/"
EXTENSION_ID = "treestyletab@piro.sakura.ne.jp"


def test_user_can_manage_pinned_extensions_on_the_sidebar(driver: Firefox):
    """
    C2652535 - Verify that extensions pinned to the sidebar are displayed in the Customize Sidebar panel and the
    Manage extensions link opens about:addons.
    """
    # Instantiate objects
    nav = Navigation(driver)
    sidebar = Sidebar(driver)
    about_addons = AboutAddons(driver)
    page = GenericPage(driver, url=TREE_STYLE_TAB_URL)

    # Navigate to the AMO page and install the desired extension
    page.open()
    page.click_on("add-to-firefox")

    # Confirm the extension installation
    nav.element_clickable("popup-notification-add")
    nav.click_on("popup-notification-add")

    # Verify the extension is pinned to the sidebar
    sidebar.expect_extension_pinned_to_sidebar(EXTENSION_ID)

    # Open the Customize Sidebar panel and click Manage Extensions
    sidebar.click_customize_sidebar()
    sidebar.click_manage_extensions()

    # Verify about:addons is opened in the new tab
    sidebar.switch_to_new_tab()
    nav.url_contains("about:addons")
