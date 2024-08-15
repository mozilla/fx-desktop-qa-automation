from selenium.webdriver import Firefox

from modules.browser_object import PanelUi

def test_clear_recent_history_displayed(driver: Firefox):
    """
    C172043: Clear recent history panel displayed
    """
    panel_ui = PanelUi(driver).open()

    panel_ui.open_panel_menu()
    with driver.context(driver.CONTEXT_CHROME):
        panel_ui.get_element("panel-ui-history").click()

        panel_ui.element_exists("clear-recent-history")
        panel_ui.element_visible("clear-recent-history")
        panel_ui.element_clickable("clear-recent-history")