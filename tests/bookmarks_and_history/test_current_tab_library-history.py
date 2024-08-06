from selenium.webdriver import Firefox

from modules.browser_object_panel_ui import PanelUi
from modules.util import Utilities

YOUTUBE_URL = "https://www.youtube.com/"


def test_websites_visited_in_current_tab_is_displayed_in_history_library(
    driver: Firefox,
):
    """
    C118800 - Verify that the recently opened website is displayed in the History submenu in Library
    """

    panel_ui = PanelUi(driver).open()
    util = Utilities()

    driver.get(YOUTUBE_URL)

    panel_ui.open_manage_history()
    # with driver.context(driver.CONTEXT_CHROME):
    #     driver.switch_to.window(driver.window_handles[-1])
    #     util.write_html_content(file_name="history", driver=driver, chrome=True)
    #     driver.find_element("id", "maintenanceButton").click()
