import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, PanelUi, Sidebar, TabBar

URL = "about:robots"
BOOKMARK_TITLE = "Gort! Klaatu barada nikto!"


@pytest.fixture()
def test_case():
    return "2652388"


def test_sidebar_vertical_tabs_can_be_bookmarked(driver: Firefox):
    """
    C2652388 - Verify that vertical tabs in the sidebar can be bookmarked.
    """
    # Instantiate objects
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)
    panel = PanelUi(driver)

    # Enable vertical tabs via toolbar context menu
    nav.toggle_vertical_tabs()

    # Navigate to a URL in the current tab
    tabs.open_urls_in_tabs([URL], open_first_in_current_tab=True)

    # Right-click the tab in the sidebar and verify "Bookmark Tab" option is displayed
    tabs.context_click(tabs.get_tab(1))
    context_menu.element_visible("context-menu-bookmark-tab")

    # Click Bookmark Tab, close the context menu, then save via the Add Bookmark dialog.
    # The dialog renders inside browser.dialogFrame > #document > dialog#bookmarkpropertiesdialog (shadow root),
    # so JS is used to pierce through contentDocument and shadow DOM to click Save.
    context_menu.click_context_item("context-menu-bookmark-tab")
    tabs.hide_popup("tabContextMenu")
    with driver.context(driver.CONTEXT_CHROME):
        nav.wait.until(
            lambda _: driver.execute_script(
                "const cd = document.querySelector('browser.dialogFrame')?.contentDocument;"
                "const btn = cd?.querySelector('dialog#bookmarkpropertiesdialog')"
                "?.shadowRoot?.querySelector('button[dlgtype=\"accept\"]');"
                "if (btn) { btn.click(); return true; }"
            )
        )

    # Verify the tab is bookmarked and present in the bookmarks list
    panel.open_bookmarks_panel_from_hamburger_menu()
    panel.verify_bookmark_exists_in_hamburger_menu(BOOKMARK_TITLE)
