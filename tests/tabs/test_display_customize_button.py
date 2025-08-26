import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object_panel_ui import PanelUi
from modules.browser_object_tabbar import TabBar
from modules.page_object import ExamplePage


@pytest.fixture()
def test_case():
    return "134463"


def test_customize_button_displayed_in_tab_bar(driver: Firefox):
    """
    C134463 - Verify that the Customize button is displayed in the tab bar
    and the Customize tab persists when switching tabs.
    """

    panel_ui = PanelUi(driver)
    tabs = TabBar(driver)

    # Open an initial example page
    example = ExamplePage(driver)
    example.open()

    # Open customize firefox toolbar tab
    panel_ui.open_panel_menu()
    panel_ui.navigate_to_customize_toolbar()

    tabs.click_tab_by_index(1)

    # Verify that the customize firefox tab is open in background
    with driver.context(driver.CONTEXT_CHROME):
        customize_tab = tabs.get_tab(2)
        assert customize_tab is not None, "Customize tab should still exist."
        assert tabs.get_tab_title(customize_tab) == "Customize Firefox"
        assert customize_tab.get_attribute("visuallyselected") != "true", (
            "Customize tab should be unfocused."
        )

    # Verify that the customize firefox tab is opened and correct
    example.switch_to_new_tab()
    with driver.context(driver.CONTEXT_CHROME):
        element = driver.find_element(By.ID, "customization-container")
        assert element, "element not found"
