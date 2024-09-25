import re
from time import sleep
from typing import List

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation
from modules.classes.autofill_base import AutofillAddressBase
from modules.classes.credit_card import CreditCardBase
from modules.components.dropdown import Dropdown
from modules.page_base import BasePage


class AboutPrefs(BasePage):
    """
    Page Object Model for about:preferences

    Attributes
    ----------
    driver: selenium.webdriver.Firefox
        WebDriver object under test
    """

    URL_TEMPLATE = "about:preferences#{category}"
    iframe = None

    # number of tabs to reach the country tab
    TABS_TO_COUNTRY = 6
    TABS_TO_SAVE_CC = 5

    def search_engine_dropdown(self) -> Dropdown:
        """Returns the Dropdown region for search engine prefs"""
        return Dropdown(
            self, self.driver, root=self.get_element("search-engine-dropdown-root")
        )

    def find_in_settings(self, term: str) -> BasePage:
        """Search via the Find in Settings bar, return self."""
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
        """Sets the country value in the autofill view"""
        for _ in range(self.TABS_TO_COUNTRY):
            self.actions.send_keys(Keys.TAB).perform()

        self.actions.send_keys(country)

        for _ in range(self.TABS_TO_COUNTRY):
            self.perform_key_combo(Keys.SHIFT, Keys.TAB)

        return self

    def extract_content_from_html(self, initial_string: str) -> AutofillAddressBase:
        """
        Takes the raw innerHTML and uses regex to filter out the tags.

        >[^<]+<"
        - > match the closing tag
        - [^<] match anything that isnt the < tag
        - +< matches the opening tag

        ...

        Attributes
        ----------
        initial_string: str
            The raw innerHTML content extracted
        """
        text = re.findall(r">[^<]+<", initial_string)
        clean_text = [s[1:-1] for s in text]
        return clean_text[0]

    def extract_and_split_text(self, text: str) -> List[str]:
        """
        Takes the raw text and strips it of any extra spaces and splits it by the character ','

        Attributes
        ----------
        text: str
            The raw text extracted from the HTML content, filtered
        """
        return [item.strip() for item in text.split(",")]

    def organize_data_into_obj(self, observed_text: List[str]) -> AutofillAddressBase:
        """
        Takes a list of text that has been split into an array and instantiates an AutofillAddressBase object

        ...

        Attributes
        ----------
        observed_text: List[str]
            A list that contains the text for each of the fields of data in an object
        """
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
        """
        Takes the sample autofill object and fills it into the popup panel in the about:prefs section
        under saved addresses.

        ...

        Attributes
        ----------
        autofill_info: AutofillAddressBase
            The object containing all of the sample data
        """
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

    def fill_cc_panel_information(
        self, credit_card_fill_information: CreditCardBase
    ) -> BasePage:
        """
        Takes the sample cc object and fills it into the popup panel in the about:prefs section
        under saved payment methods.

        ...

        Attributes
        ----------
        credit_card_fill_information: CreditCardBase
            The object containing all of the sample data
        """
        fields = {
            "card_number": credit_card_fill_information.card_number,
            "expiration_month": credit_card_fill_information.expiration_month,
            "expiration_year": f"20{credit_card_fill_information.expiration_year}",
            "name": credit_card_fill_information.name,
        }

        for field in fields:
            self.actions.send_keys(fields[field] + Keys.TAB).perform()

        # Press tab again to navigate to the next field (this accounts for the second tab after the name field)
        self.actions.send_keys(Keys.TAB).perform()
        # Finally, press enter
        self.actions.send_keys(Keys.ENTER).perform()

    def get_saved_payments_popup_iframe(self) -> WebElement:
        """
        Returns the iframe object for the dialog panel in the popup
        """
        self.get_element("prefs-button", labels=["Saved payment methods"]).click()
        iframe = self.get_element("browser-popup")
        return iframe

    def update_cc_field_panel(self, num_tabs: int, new_info: str) -> BasePage:
        """
        Updates a field in the credit card popup panel in about:prefs by pressing the number of tabs and sending the new information
        ...

        Attributes
        ----------
        autofill_info: AutofillAddressBase
            The object containing all of the sample date
        """
        for _ in range(num_tabs):
            self.actions.send_keys(Keys.TAB).perform()

        self.actions.send_keys(new_info).perform()

        for _ in range(self.TABS_TO_SAVE_CC - num_tabs):
            self.actions.send_keys(Keys.TAB).perform()

        self.actions.send_keys(Keys.ENTER).perform()

    def get_save_addresses_popup_iframe(self) -> WebElement:
        """
        Returns the iframe object for the dialog panel in the popup
        """
        self.get_element("prefs-button", labels=["Saved addresses"]).click()
        iframe = self.get_element("browser-popup")
        return iframe

    def get_clear_cookie_data_value(self) -> int:
        """
        With the 'Clear browsing data and cookies' popup open,
        returns the <memory used> value of the option for 'Cookies and site data (<memory used>)'.
        The <memory used> value for no cookies is '0 bytes', otherwise values are '### MB', or '### KB'
        """
        # Find the dialog option elements containing the checkbox label
        options = self.get_elements("clear-data-dialog-options")

        # Extract the text from the label the second option
        second_option = options[1]
        label_text = second_option.text
        print(f"The text of the option is: {label_text}")

        # Use a regular expression to find the memory usage
        match = re.search(r"\d+", label_text)

        if match:
            number_str = match.group()  # Extract the matched number as a string
            number = int(number_str)  # Convert the number to an integer
            print(f"The extracted value is: {number}")
            return number
        else:
            print("No number found in the string")

    def get_manage_data_site_element(self, site: str) -> WebElement:
        """
        Returns the WebElement for the given site in the manage site data popup
        """
        element = self.get_element("manage-cookies-site", labels=[site])
        return element

    def get_iframe(self) -> WebElement:
        """
        Gets the webelement for the iframe that commonly appears in about:preferences
        """
        return self.get_element("browser-popup")

    def set_alternative_language(self, lang_code: str) -> BasePage:
        """Changes the browser language"""
        self.get_element("language-set-alternative-button").click()
        self.driver.switch_to.frame(self.get_iframe())

        # Download the language options
        select_language = self.get_element("language-settings-select")
        select_language.click()
        search_languages = self.get_element("language-settings-search")
        search_languages.click()
        select_language.click()

        # Select the language, add, and make sure it appears
        select_language.click()
        self.get_element("language-option-by-code", labels=[lang_code]).click()
        select_language.click()
        self.get_element("language-settings-add-button").click()
        self.element_attribute_contains(
            "language-added-list", "last-selected", f"locale-{lang_code}"
        )

        self.get_element("language-settings-ok").click()
        return self

    def get_history_menulist(self) -> WebElement:
        """
        Gets the webelement for the list of history items that appear in about:preferences
        """
        return self.get_element("history_menulist")

    def import_bookmarks(self, browser_name: str) -> BasePage:
        """
        Press the import browser data button
        """
        MAX_TRIES = 16

        self.click_on("import-browser-data")
        sleep(2)
        tries = 0

        # Keep cycling through the options until you get it
        # Using keys for most of this because clicking elements is flaky for some reason
        while (
            browser_name.lower()
            not in self.get_element("browser-profile-selector").text.lower()
            and tries < MAX_TRIES
        ):
            self.actions.send_keys(" ").perform()
            for _ in range(tries):
                self.actions.send_keys(Keys.DOWN).perform()
            self.actions.send_keys(" ").perform()
            sleep(1)
            tries += 1

        self.click_on("migration-import-button")

        # There are two messages that indicate a successful migration
        self.wait.until(
            lambda _: self.get_element("migration-progress-header").text
            in ["Data Imported Successfully", "Data Import Complete"]
        )
        self.actions.send_keys(" ").perform()
        return self

    def get_all_saved_cc_profiles(self) -> List[WebElement]:
        """Gets the saved credit card profiles in the cc panel"""
        if self.iframe:
            with self.driver.switch_to.frame(self.iframe):
                return self.get_element("cc-saved-options", multiple=True)
        else:
            return self.get_element("cc-saved-options", multiple=True)

    def click_popup_panel_button(self, field: str) -> BasePage:
        """Clicks the popup panel button for the specified field"""
        if self.iframe:
            with self.driver.switch_to.frame(self.iframe):
                self.get_element("panel-popup-button", labels=[field]).click()
        else:
            self.get_element("panel-popup-button", labels=[field]).click()
        return self


class AboutAddons(BasePage):
    """
    The POM for the about:addons page

    Attributes
    ----------
    driver: selenium.webdriver.Firefox
        WebDriver object under test
    """

    URL_TEMPLATE = "about:addons"

    def choose_sidebar_option(self, option: str):
        """
        Clicks the corresponding sidebar option from the about:addons page.
        """
        self.get_element("sidebar-options", labels=[option]).click()

    def activate_theme(
        self, nav: Navigation, theme_name: str, intended_color: str, perform_assert=True
    ):
        """
        Clicks the theme card and presses enable. Then verifies that the theme is the correct color.

        Attributes
        ----------
        nav: Navigation
            The navgiation object
        theme_name: str
            The name of the theme to press
        intended_color: str
            The RGB string that is the intended color of the element
        """
        self.get_element("theme-card", labels=[theme_name]).click()
        self.get_element("enable-theme").click()

        self.expect(
            EC.text_to_be_present_in_element_attribute(
                self.get_selector("enable-theme"), "innerText", "Disable"
            )
        )

        with self.driver.context(self.driver.CONTEXT_CHROME):
            navigation_component = nav.get_element("navigation-background-component")
            background_color = navigation_component.value_of_css_property(
                "background-color"
            )
            if perform_assert:
                assert background_color == intended_color
            else:
                return background_color

    def enabled_theme_matches(self, expected_theme: str) -> bool:
        """
        Check the enabled theme name against any string.
        """

        enabled_theme = self.get_element("enabled-theme-title").get_attribute(
            "innerText"
        )
        return enabled_theme == expected_theme

    def check_theme_has_changed(self, original_theme: str) -> BasePage:
        """
        Ensure that the theme has changed.
        """
        assert not self.enabled_theme_matches(original_theme)
        return self
