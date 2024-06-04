import re
from time import sleep
from typing import List

from pypom import Region
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from modules.classes.autofill_base import AutofillAddressBase
from modules.classes.credit_card import CreditCardBase
from modules.page_base import BasePage
from modules.util import PomUtils


class AboutPrefs(BasePage):
    """Page Object Model for about:preferences"""

    URL_TEMPLATE = "about:preferences#{category}"

    # number of tabs to reach the country tab
    TABS_TO_COUNTRY = 6

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

    def press_button_get_popup_dialog_iframe(self, button_label: str) -> WebElement:
        """
        Returns the iframe object for the dialog panel in the popup after pressing some button that triggers a popup
        """
        self.get_element("prefs-button", labels=[button_label]).click()
        iframe = self.get_element("browser-popup")
        return iframe

    def set_country_autofill_panel(self, country: str) -> BasePage:
        for _ in range(self.TABS_TO_COUNTRY):
            self.actions.send_keys(Keys.TAB).perform()

        self.actions.send_keys(country)

        for _ in range(self.TABS_TO_COUNTRY):
            self.perform_key_combo(Keys.SHIFT, Keys.TAB)

        return self

    def extract_content_from_html(self, initial_string: str) -> str:
        text = re.findall(r">[^<]+<", initial_string)
        clean_text = [s[1:-1] for s in text]
        return clean_text[0]

    def extract_and_split_text(self, text: str) -> List[str]:
        return [item.strip() for item in text.split(",")]

    def organize_data_into_obj(self, observed_text: List[str]) -> AutofillAddressBase:
        if len(observed_text) < 8:
            return None

        name = observed_text[0]
        address = observed_text[1]
        address_level_2 = observed_text[2]
        organization = observed_text[3]
        address_level_1 = observed_text[4]
        country = observed_text[5]
        postal_code = observed_text[6]
        telephone = observed_text[7]
        email = observed_text[8]

        return AutofillAddressBase(
            name,
            organization,
            address,
            address_level_2,
            address_level_1,
            postal_code,
            country,
            email,
            telephone,
        )

    def fill_autofill_panel_information(
        self, autofill_info: AutofillAddressBase
    ) -> BasePage:
        fields = {
            "name": autofill_info.name,
            "organization": autofill_info.organization,
            "street-address": autofill_info.street_address,
            "address-level2": autofill_info.address_level_2,
            "address-level1": autofill_info.address_level_1,
            "postal-code": autofill_info.postal_code,
            "country": "Canada" if autofill_info.country == "CA" else "United States",
            "tel": autofill_info.telephone,
            "email": autofill_info.email,
        }

        self.set_country_autofill_panel(fields["country"])

        for field in fields:
            if field == "country":
                self.actions.send_keys(Keys.TAB)
                continue
            self.actions.send_keys(fields[field] + Keys.TAB).perform()
        self.actions.send_keys(Keys.TAB).perform()
        self.actions.send_keys(Keys.ENTER).perform()
        return self
