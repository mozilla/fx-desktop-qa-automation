import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, Sidebar


@pytest.fixture()
def test_case():
    return "2947650"


def test_sidebar_expand_collapse_on_hover_unaffected_by_right_side_position(
    driver: Firefox,
):
    """
    C2947650 - Verify that moving the sidebar to the right side does not break
    expand/collapse on hover behaviour.
    """
    sidebar = Sidebar(driver)
    nav = Navigation(driver)

    # Enable vertical tabs via toolbar context menu
    nav.toggle_vertical_tabs()

    # Open Customize Sidebar panel
    sidebar.click_customize_sidebar()

    # Enable "Expand sidebar on hover" and move the sidebar to the right
    sidebar.click_expand_on_hover_in_panel()
    sidebar.click_move_sidebar_to_right_in_panel()

    # Close the Customize Sidebar panel so the sidebar returns to its collapsed strip state
    sidebar.click_customize_sidebar()
    sidebar.expect_sidebar_strip_collapsed()

    # Hover over the sidebar strip and verify it expands
    collapsed_width = sidebar.get_sidebar_strip_width()
    sidebar.hover("sidebar-main")
    sidebar.wait.until(lambda _: sidebar.get_sidebar_strip_width() > collapsed_width)

    # Move the mouse away and verify the sidebar collapses again
    expanded_width = sidebar.get_sidebar_strip_width()
    assert expanded_width > collapsed_width
    sidebar.hover("sidebar-button")
    sidebar.wait.until(lambda _: sidebar.get_sidebar_strip_width() < expanded_width)
