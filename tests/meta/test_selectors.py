import logging

from selenium.webdriver import Firefox

from modules.browser_object import PanelUi


def test_a_selector(driver: Firefox, version: str):
    logging.info(f"Fx version {version}")
    panel = PanelUi(driver).open()
    panel.open_panel_menu()
    with driver.context(driver.CONTEXT_CHROME):
        panel.get_element("zoom-reduce").click()
        panel.get_element("zoom-reduce").click()
        panel.get_element("zoom-enlarge").click()
        panel.get_element("zoom-reset").click()
