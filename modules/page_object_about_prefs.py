from pypom import Region
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from modules.classes.credit_card import CreditCardBase
from modules.page_base import BasePage
from modules.util import PomUtils


class AboutPrefs(BasePage):
    """Page Object Model for about:preferences"""

    URL_TEMPLATE = "about:preferences#{category}"

    class Dropdown(Region):
        def __init__(self, page, **kwargs):
            super().__init__(page, **kwargs)
            self.utils = PomUtils(self.driver)
            self.shadow_elements = self.utils.get_shadow_content(self.root)
            self.dropmarker = next(
                el for el in self.shadow_elements if el.tag_name == "dropmarker"
            )

        @property
        def loaded(self):
            return self.root if EC.element_to_be_clickable(self.root) else False

        def select_option(self, option_name):
            if not self.dropmarker.get_attribute("open") == "true":
                self.root.click()
            matching_menuitems = [
                el
                for el in self.root.find_elements(By.CSS_SELECTOR, "menuitem")
                if el.get_attribute("label") == option_name
            ]
            if len(matching_menuitems) == 0:
                return False
            elif len(matching_menuitems) == 1:
                matching_menuitems[0].click()
                self.wait.until(EC.element_to_be_selected(matching_menuitems[0]))
                return self
            else:
                raise ValueError("More than one menu item matched search string")

    def search_engine_dropdown(self) -> Dropdown:
        return self.Dropdown(self, root=self.get_element("search-engine-dropdown-root"))

    def find_in_settings(self, term: str) -> BasePage:
        search_input = self.get_element("find-in-settings-input")
        search_input.clear()
        search_input.send_keys(term)
        return self

    def verify_cc_json(
        self, cc_info_json: dict, credit_card_fill_obj: CreditCardBase
    ) -> BasePage:
        """
        Does the assertions that ensure all of the extracted information (the cc_info_json) is the same as the generated fake credit_card_fill_obj data.


        ...

        Attributes
        ----------
        cc_info_json: dict
            The dictionary that is the json representation of the extracted information from a web page
        credit_card_fill_obj: CreditCardBase
            The object that contains all of the generated information
        """
        assert cc_info_json["name"] == credit_card_fill_obj.name
        assert cc_info_json["number"][-4:] == credit_card_fill_obj.card_number[-4:]
        assert int(cc_info_json["month"]) == int(credit_card_fill_obj.expiration_month)
        return self

    def get_saved_payments_popup_iframe(self) -> WebElement:
        """
        Returns the iframe object for the dialog panel in the popup
        """
        self.get_element("prefs-button", labels=["Saved payment methods"]).click()
        iframe = self.get_element("browser-popup")
        return iframe
