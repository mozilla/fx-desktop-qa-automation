import logging
import re
from time import sleep
from typing import List

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

from modules.browser_object import Navigation
from modules.classes.autofill_base import AutofillAddressBase
from modules.classes.credit_card import CreditCardBase
from modules.components.dropdown import Dropdown
from modules.page_base import BasePage
from modules.util import Utilities


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

    def __init__(self, driver: Firefox, **kwargs):
        super().__init__(driver, **kwargs)
        self.driver = driver

    # Number of tabs to reach the country tab
    TABS_TO_COUNTRY = 6
    TABS_TO_SAVE_CC = 5

    class HttpsOnlyStatus:
        """Fake enum: return a string based on a constant name"""

        def __init__(self):
            self.HTTPS_ONLY_ALL = "httpsonly-radio-enabled"
            self.HTTPS_ONLY_PRIVATE = "httpsonly-radio-enabled-pbm"
            self.HTTPS_ONLY_DISABLED = "httpsonly-radio-disabled"

    HTTPS_ONLY_STATUS = HttpsOnlyStatus()

    # Function Organization
    # Search and Settings
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
        self.expect_element_attribute_contains(
            "language-added-list", "last-selected", f"locale-{lang_code}"
        )

        self.get_element("language-settings-ok").click()
        return self

    def select_https_only_setting(self, option_id: HttpsOnlyStatus) -> BasePage:
        """
        Click the HTTPS Only option given
        """
        self.find_in_settings("HTTPS")
        self.element_clickable(str(option_id))
        self.click_on(str(option_id))
        self.expect_element_attribute_contains(str(option_id), "checked", "")
        return self

    def set_default_zoom_level(self, zoom_percentage: int) -> BasePage:
        """
        Sets the Default Zoom level in about:preferences.
        """
        self.click_on("default-zoom-dropdown")
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.click_on("default-zoom-dropdown-value", labels=[f"{zoom_percentage}"])
        self.click_on("default-zoom-dropdown")
        return self

    def select_content_and_action(self, content_type: str, action: str) -> BasePage:
        """
        From the applications list that handles how downloaded media is used,
        select a content type and action
        """
        el = self.get_element("actions-menu", labels=[content_type])
        el.click()
        self.click_on("actions-menu-option", labels=[content_type, action])
        self.wait.until(lambda _: el.get_attribute("label") == action)
        return self

    def select_trackers_to_block(self, *options):
        """Select the trackers to block in the about:preferences page. Unchecks all first."""
        self.click_on("custom-radio")
        checkboxes = self.get_element("custom-tracker-options-parent").find_elements(
            By.TAG_NAME, "checkbox"
        )
        for checkbox in checkboxes:
            if checkbox.is_selected():
                checkbox.click()
        for option in options:
            self.click_on(option)
        return self

    def get_history_menulist(self) -> WebElement:
        """
        Gets the web element for the list of history items that appear in about:preferences
        """
        return self.get_element("history_menulist")

    # Payment and Address Management
    def verify_cc_json(
        self, cc_info_json: dict, credit_card_fill_obj: CreditCardBase
    ) -> BasePage:
        """
        Does the assertions that ensure all the extracted information (the cc_info_json) is the same as the generated fake credit_card_fill_obj data.

        ...

        Attributes
        ----------
        cc_info_json: dict
            The dictionary that is the json representation of the extracted information from a web page
        credit_card_fill_obj: CreditCardBase
            The object that contains all the generated information
        """
        assert cc_info_json["name"] == credit_card_fill_obj.name
        assert cc_info_json["number"][-4:] == credit_card_fill_obj.card_number[-4:]
        assert int(cc_info_json["month"]) == int(credit_card_fill_obj.expiration_month)
        return self

    def verify_cc_edit_saved_payments_profile(
        self, credit_card_fill_obj: CreditCardBase
    ):
        """
        Verify saved payment profile data is the same as the generated fake credit_card_fill_obj data.
        Make sure cvv is not displayed.

        Arguments:
            credit_card_fill_obj: CreditCardBase
                The object that contains all the generated information
        """
        self.switch_to_edit_saved_payments_popup_iframe()
        form_container = self.get_element("form-container")
        input_elements = form_container.find_elements(By.TAG_NAME, "input")
        expected_cc_data = [
            int(val) if val.isnumeric() else val
            for val in credit_card_fill_obj.__dict__.values()
        ]
        expected_cvv = int(credit_card_fill_obj.cvv)
        for element in input_elements:
            field_name = element.get_attribute("id")
            if field_name.startswith("cc"):
                field_value = element.get_attribute("value")
                if field_value.isnumeric():
                    field_value = int(field_value)
                assert field_value in expected_cc_data, (
                    f"{(field_name, field_value)} not found in generated data."
                )
                assert field_value != expected_cvv, "CVV is displayed."
        select_elements = form_container.find_elements(By.TAG_NAME, "select")
        for element in select_elements:
            field_name = element.get_attribute("id")
            if field_name.startswith("cc"):
                val = Select(element)
                # Only get the last two digits
                field_value = val.first_selected_option.get_attribute("value")[-2:]
                if field_value.isnumeric():
                    field_value = int(field_value)
                assert field_value in expected_cc_data, (
                    f"{(field_name, field_value)} not found in generated data."
                )
                assert field_value != expected_cvv, "CVV is displayed."
        return self

    def get_saved_payments_popup(self) -> WebElement:
        """
        Open saved payments dialog panel
        """
        return self.get_element("prefs-button", labels=["Saved payment methods"])

    def click_edit_on_dialog_element(self):
        """
        Click on edit button on dialog panel
        """
        edit_button = self.get_element(
            "panel-popup-button", labels=["autofill-manage-edit-button"]
        )
        self.expect(EC.element_to_be_clickable(edit_button))
        edit_button.click()
        return self

    def click_add_on_dialog_element(self):
        """
        Click on add button on dialog panel
        """
        add_button = self.get_element(
            "panel-popup-button", labels=["autofill-manage-add-button"]
        )
        self.expect(EC.element_to_be_clickable(add_button))
        add_button.click()
        return self

    def open_and_switch_to_saved_payments_popup(self) -> BasePage:
        """
        Open and Switch to saved payments popup frame.
        """
        saved_payments_iframe = self.get_saved_payments_popup_iframe()
        self.driver.switch_to.frame(saved_payments_iframe)
        return self

    def fill_and_save_cc_panel_information(
        self, credit_card_fill_information: CreditCardBase
    ):
        """
        Takes the sample cc object and fills it into the popup panel in the about:prefs section
        under saved payment methods.

        Arguments:
            credit_card_fill_information: The object containing all the sample data
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

    def add_entry_to_saved_payments(self, cc_data: CreditCardBase):
        """
        Takes the sample AutofillAddressBase object and adds an entry to the saved addresses list.
        Switches the appropriate frames to accommodate the operation.
        Exits after adding entry

        Arguments:
            cc_data: The object containing all the sample data
        """
        self.switch_to_saved_payments_popup_iframe()
        self.fill_and_save_cc_panel_information(cc_data)
        self.switch_to_default_frame()
        self.close_dialog_box()
        return self

    def close_dialog_box(self):
        """Close dialog box for saved addresses or payments."""
        self.element_clickable("panel-popup-button", labels=["close-button"])
        self.get_element("panel-popup-button", labels=["close-button"]).click()
        return self

    def update_cc_field_panel(self, field_name: str, value: str | int) -> BasePage:
        """
        Updates a field in the credit card popup panel in about:prefs
        Change value of the field_name given
        """

        fields = {
            "card_number": "cc-number",
            "expiration_month": "cc-exp-month",
            "expiration_year": "cc-exp-year",
            "name": "cc-name",
        }
        if field_name not in fields.keys():
            raise ValueError(
                f"{field_name} is not a valid field name for the cc dialog form."
            )
        self.switch_to_edit_saved_payments_popup_iframe()
        value_field = self.find_element(By.ID, fields[field_name])
        if value_field.tag_name != "select":
            value_field.clear()
        value_field.send_keys(value)
        logging.warning(f"updating: {value_field.get_attribute('value')} -> {value}")
        self.get_element("save-button").click()
        return self

    def get_saved_addresses_popup(self) -> WebElement:
        """
        Returns saved addresses button element
        """
        return self.get_element("prefs-button", labels=["Saved addresses"])

    def open_and_switch_to_saved_addresses_popup(self) -> BasePage:
        """
        Open and Switch to saved addresses popup frame.
        """
        saved_address_iframe = self.get_saved_addresses_popup_iframe()
        self.driver.switch_to.frame(saved_address_iframe)
        return self

    def add_entry_to_saved_addresses(self, address_data: AutofillAddressBase):
        """
        Takes the sample AutofillAddressBase object and adds an entry to the saved addresses list.
        Switches the appropriate frames to accommodate the operation.
        Exits after adding entry

        Arguments:
            address_data: The object containing all the sample data
        """

        self.switch_to_edit_saved_addresses_popup_iframe()
        self.fill_and_save_address_panel_information(address_data)
        self.switch_to_default_frame()
        self.close_dialog_box()
        return self

    def get_all_saved_cc_profiles(self) -> List[WebElement]:
        """Gets the saved credit card profiles in the cc panel"""
        self.switch_to_saved_payments_popup_iframe()
        element = Select(self.get_element("cc-saved-options"))
        return element.options

    def get_all_saved_address_profiles(self) -> List[WebElement]:
        """Gets the saved credit card profiles in the cc panel"""
        self.switch_to_saved_addresses_popup_iframe()
        select_el = self.get_element("address-saved-options")
        if len(select_el.get_attribute("innerHTML")) > 1:
            return Select(select_el).options
        return []

    def extract_address_data_from_saved_addresses_entry(
        self, util: Utilities, region: str = "US"
    ) -> AutofillAddressBase:
        """
        Extracts the data from the saved addresses entry to a AutofillAddressBase object.

        Arguments:
            util: Utility instance
            region: country code in use
        """
        self.switch_to_edit_saved_addresses_popup_iframe()
        fields = {
            "name": "",
            "organization": "",
            "street-address": "",
            "address-level2": "",
            "address-level1": "",
            "postal-code": "",
            "tel": "",
            "country": "",
            "email": "",
        }

        for key in fields.keys():
            el = self.find_element(By.ID, key)
            if el.tag_name == "select":
                fields[key] = Select(el).first_selected_option.text
            else:
                fields[key] = el.get_attribute("value")

        return AutofillAddressBase(
            name=fields.get("name"),
            given_name=fields.get("name", "").split()[0],
            family_name=fields.get("name", "").split()[1],
            organization=fields.get("organization"),
            street_address=fields.get("street-address"),
            address_level_2=fields.get("address-level2"),
            address_level_1=fields.get("address-level1"),
            postal_code=fields.get("postal-code"),
            country=fields.get("country"),
            country_code=region,
            email=fields.get("email"),
            telephone=util.normalize_regional_phone_numbers(fields.get("tel"), region),
        )

    # UI Navigation and Iframe Handling
    def get_saved_payments_popup_iframe(self) -> WebElement:
        """
        Returns the iframe object for the dialog panel in the popup
        """
        self.get_saved_payments_popup().click()
        iframe = self.get_element("browser-popup")
        return iframe

    def switch_to_edit_saved_payments_popup_iframe(self) -> BasePage:
        """
        Switch to form iframe to edit saved payments.
        """
        self.switch_to_default_frame()
        self.switch_to_iframe(2)
        return self

    def press_button_get_popup_dialog_iframe(self, button_label: str) -> WebElement:
        """
        Returns the iframe object for the dialog panel in the popup after pressing some button that triggers a popup
        """
        self.get_element("prefs-button", labels=[button_label]).click()
        iframe = self.get_element("browser-popup")
        return iframe

    def get_saved_addresses_popup_iframe(self) -> WebElement:
        """
        Returns the iframe object for the dialog panel in the popup
        """
        self.get_saved_addresses_popup().click()
        iframe = self.get_element("browser-popup")
        return iframe

    def switch_to_saved_addresses_popup_iframe(self) -> BasePage:
        """
        switch to save addresses popup frame.
        """
        self.switch_to_default_frame()
        self.switch_to_iframe(1)
        return self

    def switch_to_saved_payments_popup_iframe(self) -> BasePage:
        """
        switch to save payments popup frame.
        """
        self.switch_to_default_frame()
        self.switch_to_iframe(1)
        return self

    def switch_to_edit_saved_addresses_popup_iframe(self) -> BasePage:
        """
        Switch to form iframe to edit saved addresses.
        """
        self.switch_to_default_frame()
        self.switch_to_iframe(2)
        return self

    def get_iframe(self) -> WebElement:
        """
        Gets the webelement for the iframe that commonly appears in about:preferences
        """
        return self.get_element("browser-popup")

    def get_password_exceptions_popup_iframe(self) -> WebElement:
        """
        Returns the iframe object for the Password Exceptions dialog panel in the popup.
        """
        # Click on the "Password Exceptions" button
        self.get_element("logins-exceptions").click()
        # Get the iframe element for the popup
        iframe = self.get_element("browser-popup")
        return iframe

    # Data Extraction and Processing
    def set_country_autofill_panel(self, country: str) -> BasePage:
        """Sets the country value in the autofill view"""
        select_country = Select(self.driver.find_element(By.ID, "country"))
        select_country.select_by_value(country)
        return self

    def fill_and_save_address_panel_information(
        self, address_data: AutofillAddressBase
    ) -> BasePage:
        """
        Takes the sample AutofillAddressBase object and fills it into the popup panel in the about:prefs section
        under saved addresses methods.

        Arguments:
            address_data: The object containing all the sample data
        """
        fields = {
            "name": address_data.name,
            "organization": address_data.organization,
            "street-address": address_data.street_address,
            "address-level2": address_data.address_level_2,
            "address-level1": address_data.address_level_1,
            "postal-code": address_data.postal_code,
            "tel": address_data.telephone,
            "email": address_data.email,
        }

        self.set_country_autofill_panel(address_data.country_code)
        form_element = self.get_element("form-container")
        children = [
            x.get_attribute("id")
            for x in form_element.find_elements(By.CSS_SELECTOR, "*")
        ]

        for key, val in fields.items():
            if key in children:
                form_element.find_element(By.ID, key).send_keys(val)
        self.get_element("save-button").click()
        return self

    def get_clear_cookie_data_value(self) -> int | None:
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

    # Utility Functions
    def import_bookmarks(self, browser_name: str, platform) -> BasePage:
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
        sleep(1)

        # On Windows, Tab to and use the Skip button
        if platform.lower().startswith("win"):
            for _ in range(3):
                self.actions.send_keys(Keys.TAB).perform()
            self.actions.send_keys(Keys.RETURN).perform()

        # There are two messages that indicate a successful migration
        self.wait.until(
            lambda _: self.get_element("migration-progress-header").text
            in ["Data imported successfully", "Data import complete"]
        )
        self.actions.send_keys(" ").perform()
        return self

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
        sleep(1)
        self.get_element("sidebar-options", labels=[option]).click()

    def activate_theme(
        self, nav: Navigation, theme_name: str, intended_color: str, perform_assert=True
    ):
        """
        Clicks the theme card and presses enable. Then verifies that the theme is the correct color.

        Attributes
        ----------
        nav: Navigation
            The navigation object
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

    def is_devedition(self):
        active_theme_el = self.driver.find_element(
            By.CSS_SELECTOR, ".card.addon[active] h3.addon-name"
        )
        active_theme_name = active_theme_el.text.lower()
        return "dark" in active_theme_name or "developer edition" in active_theme_name

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
        Ensure the theme has changed.
        """
        assert not self.enabled_theme_matches(original_theme)
        return self
