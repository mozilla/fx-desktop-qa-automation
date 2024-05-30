from typing import List

from selenium.webdriver import Firefox
from selenium.webdriver.remote.webelement import WebElement

from modules.page_base import BasePage


class AboutPrefsCcPopup(BasePage):
    """
    Browser object for the popup upon pressing the Saved Payment Methods button in settings.
    """

    URL_TEMPLATE = ""
    iframe = None

    def __init__(self, driver: Firefox, iframe: WebElement, **kwargs):
        super().__init__(driver, **kwargs)
        self.iframe = iframe

    def get_all_saved_cc_profiles(self) -> List[WebElement] | WebElement:
        """
        Gets the saved profiles in the cc panel
        """
        return self.get_element("cc-saved-options", multiple=True)

    def click_popup_panel_button(self, field: str) -> BasePage:
        """
        Clicks the popup panel in the settings for Saved Payment Methods button
        """
        self.get_element("cc-popup-button", labels=[field]).click()
        return self
