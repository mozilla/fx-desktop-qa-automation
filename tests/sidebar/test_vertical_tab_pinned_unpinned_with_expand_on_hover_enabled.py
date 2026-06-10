import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, Sidebar, TabBar


@pytest.fixture()
def test_case():
    return "2947808"


def test_vertical_tab_pinned_unpinned_with_expand_on_hover_enabled(driver: Firefox):
    """
    C2947808 - Verify that a vertical tab can be pinned and unpinned with "Expand sidebar on hover" enabled in the
    sidebar, with the sidebar positioned on the left and on the right.
    """
    # Instantiate objects
    sidebar = Sidebar(driver)
    nav = Navigation(driver)
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)

    # Enable vertical tabs via toolbar context menu
    nav.toggle_vertical_tabs()

    # Open Customize Sidebar panel, enable "Expand sidebar on hover", then close the panel
    sidebar.click_customize_sidebar()
    sidebar.click_expand_on_hover_in_panel()
    sidebar.click_customize_sidebar()

    # Left side: pin a tab and verify, then unpin and verify
    first_tab = tabs.get_tab(1)
    tabs.context_click(first_tab)
    context_menu.click_and_hide_menu("context-menu-pin-tab")
    assert tabs.is_pinned(first_tab)

    tabs.context_click(first_tab)
    context_menu.click_and_hide_menu("context-menu-unpin-tab")
    assert not tabs.is_pinned(first_tab)

    # Move sidebar to the right and wait for it to stabilize
    sidebar.move_sidebar_to_right()
    sidebar.expect_sidebar_strip_collapsed()

    # Right side: pin a tab and verify, then unpin and verify
    first_tab = tabs.get_tab(1)
    tabs.context_click(first_tab)
    context_menu.click_and_hide_menu("context-menu-pin-tab")
    assert tabs.is_pinned(first_tab)

    tabs.context_click(first_tab)
    context_menu.click_and_hide_menu("context-menu-unpin-tab")
    assert not tabs.is_pinned(first_tab)
