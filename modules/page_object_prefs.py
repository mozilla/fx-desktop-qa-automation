import json
from time import sleep
from typing import List, Literal

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
from modules.util import BrowserActions, Utilities

HttpsOnlyMode = Literal["all", "private", "disabled"]
DohMode = Literal["default", "custom"]


class AboutPrefs(BasePage):
    """
    Page Object Model for about:preferences

    Attributes
    ----------
    driver: selenium.webdriver.Firefox
        WebDriver object under test
    """

    URL_TEMPLATE = "about:preferences#{category}"
    OPTIONS_MAX = 12
    iframe = None

    def __init__(self, driver: Firefox, **kwargs):
        super().__init__(driver, **kwargs)
        self.driver = driver

    # Number of tabs to reach the country tab
    TABS_TO_COUNTRY = 6
    TABS_TO_SAVE_CC = 5
    ZOOM_LEVELS = [
        30,
        50,
        67,
        80,
        90,
        100,
        110,
        120,
        133,
        150,
        170,
        200,
        240,
        300,
        400,
        500,
    ]

    HTTPS_ONLY_RADIO_IDS = {
        "all": "httpsonly-radio-enabled",
        "private": "httpsonly-radio-enabled-pbm",
        "disabled": "httpsonly-radio-disabled",
    }

    DOH_RADIO_IDS = {
        "default": "doh-radio-default",
        "custom": "doh-radio-custom",
    }

    # Function Organization
    # Search and Settings

    def select_search_suggestions_in_address_bar(self, value: bool = True) -> BasePage:
        """
        Selects the search suggestions in the Address Bar checkbox according to the value given.
        """
        checkbox = self.get_element("show-suggestions")
        awesome_bar_checkbox = self.get_element("show-suggestions-awesomebar")
        checked = bool(checkbox.get_attribute("checked"))
        if value != checked:
            checkbox.click()
        if value and not awesome_bar_checkbox.get_attribute("checked"):
            awesome_bar_checkbox.click()
        return self

    def search_engine_dropdown(self) -> Dropdown:
        """Returns the Dropdown region for search engine prefs"""
        return Dropdown(self, root=self.get_element("search-engine-dropdown-root"))

    def select_default_search_engine_by_key(self, option: str) -> BasePage:
        """Open the Default Search Engine dropdown directly and use keys to choose"""
        for i in range(self.OPTIONS_MAX):
            self.click_on("default-engine-dropdown")
            for _ in range(i):
                self.actions.send_keys(Keys.DOWN)
            self.actions.send_keys(Keys.ENTER).perform()
            if self.get_element("select-wrapper-button").text == option:
                break
        assert self.get_element("select-wrapper-button").text == option
        return self

    def find_in_settings(self, term: str) -> BasePage:
        """Search via the Find in Settings bar, return self."""
        search_input = self.get_element("find-in-settings-input")
        search_input.clear()
        search_input.send_keys(term)
        return self

    def enable_private_window_suggestions(self):
        """Enable 'Show search suggestions in Private Windows' if not already checked."""

        checkbox = self.get_element("search-suggestion-in-private-windows")
        if checkbox.get_attribute("checked") != "true":
            checkbox.click()
        return self

    def select_search_engine_from_tree(self, engine_name: str) -> BasePage:
        """
        Select a search engine from the 'Search Shortcuts' list in about:preferences.
        Note:
            This method handles browser UI built with Firefox’s internal XUL TreeView API,
            where items are generated virtually rather than as standard DOM nodes. Since
            Selenium cannot interact with these virtual rows directly, this method scrolls
            to the table and delegates selection to a JavaScript-based helper.
        Argument:
            engine_name (str): Name of the search engine to select (e.g., "DuckDuckGo")
        """
        search_shortcuts_group = self.get_element("search-shortcuts-group")
        engine_list = self.get_element(
            "search-engine-list", parent_element=search_shortcuts_group
        )
        return self._select_engine_with_javascript(engine_list, engine_name)

    def _select_engine_with_javascript(self, engine_list, engine_name: str) -> BasePage:
        """
        Select a search engine from a XUL TreeView-backed list via JavaScript.
        Note:
            The 'Search Shortcuts' table is rendered using Firefox’s internal TreeView API,
            not the standard DOM. Therefore, Selenium cannot access or click individual rows.
            This method executes JavaScript to loop through the TreeView rows and programmatically
            select the row that matches the given engine name.
        Arguments:
            engine_list: WebElement representing the XUL tree container.
            engine_name (str): Search engine name to select (case-insensitive match).
        Raises:
            Exception: If no matching search engine is found in the TreeView.
        """
        js = """
        let tree = arguments[0];
        let name = arguments[1].toLowerCase();
        let view = tree.view;
        for (let i = 0; i < view.rowCount; i++) {
            let text = view.getCellText(i, tree.columns.getNamedColumn("engineName"));
            if (text && text.toLowerCase().includes(name)) {
                view.selection.select(i);
                tree.ensureRowIsVisible(i);
                return true;
            }
        }
        return false;
        """

        found = self.driver.execute_script(js, engine_list, engine_name)
        if not found:
            raise Exception(
                f"Search engine '{engine_name}' not found in Search Shortcuts table."
            )
        return self

    @BasePage.context_chrome
    def remove_search_engine(self, engine_name: str) -> BasePage:
        """
        Remove a search engine from the 'Search Shortcuts' list in about:preferences.
        Argument:
            engine_name (str): Name of the search engine to remove (e.g., "DuckDuckGo")
        """
        self.element_visible("remove-search-engine-button")
        self.click_on("remove-search-engine-button")
        return self

    @BasePage.context_chrome
    def restore_default_search_engines(self) -> BasePage:
        """
        Restore the default search engines in the 'Search Shortcuts' list in about:preferences.
        """
        self.element_visible("restore-default-search-engines-button")
        self.click_on("restore-default-search-engines-button")
        return self

    @BasePage.context_content
    def verify_clipboard_suggestion_enabled(self) -> None:
        checkbox = self.get_element("clipboard-suggestion-checkbox")
        is_checked = checkbox.get_attribute("checked") in ("true", "checked", "")
        assert is_checked, "Expected clipboardSuggestion checkbox to be checked"

    def set_alternative_language(self, lang_code: str) -> BasePage:
        """Sets the browser language via the Preferred language moz-select.

        Firefox applies the locale live once the dropdown value changes.
        """
        Select(self.get_element("browser-language-preferred-select")).select_by_value(
            lang_code
        )
        self.element_attribute_is("browser-language-preferred", "value", lang_code)
        return self

    def open_doh_advanced(self) -> BasePage:
        """Open the DoH Advanced settings sub-pane.

        The button toggles — call once per test.
        """
        self.click_on("doh-advanced-button")
        return self

    def select_doh_protection_level(self, level: DohMode) -> BasePage:
        """Select a DNS over HTTPS mode. Requires `open_doh_advanced` first."""
        option_id = self.DOH_RADIO_IDS[level]
        self.element_clickable(option_id)
        self.click_on(f"{option_id}-input")
        self.element_attribute_contains(option_id, "checked", "")
        return self

    def verify_doh_provider(self, provider_name: str) -> BasePage:
        """Wait until the DoH status box reports the given provider name."""
        self.element_attribute_contains(
            "doh-status-box", "data-l10n-args", provider_name
        )
        return self

    def open_connection_advanced(self) -> BasePage:
        """Open Connection and software security > Advanced settings sub-pane.

        The HTTPS-Only Mode card lives behind this button. Call once per
        test; the sub-pane state persists across window switches.
        """
        self.click_on("connection-advanced-button")
        return self

    def select_https_only_setting(self, mode: HttpsOnlyMode) -> BasePage:
        """Select an HTTPS-Only Mode radio. Requires `open_connection_advanced` first."""
        option_id = self.HTTPS_ONLY_RADIO_IDS[mode]
        self.element_clickable(option_id)
        self.click_on(f"{option_id}-input")
        self.element_attribute_contains(option_id, "checked", "")
        return self

    def click_zoom_text_only(self) -> BasePage:
        """
        Toggles the Zoom Text Only checkbox in about:preferences.
        Uses JS to pierce the moz-checkbox shadow root.
        """
        moz_checkbox = self.get_element("zoom-text-only")
        self.driver.execute_script("arguments[0].click()", moz_checkbox)
        return self

    def set_default_zoom_level(self, zoom_percentage: int) -> BasePage:
        """
        Sets the Default Zoom level in about:preferences.
        Gets the inner <select> from moz-select's shadow root and uses
        Selenium's Select class to choose the target zoom level.
        """
        moz_select = self.get_element("default-zoom-dropdown")
        inner_select = self.driver.execute_script(
            "return arguments[0].shadowRoot.querySelector('select')",
            moz_select,
        )
        Select(inner_select).select_by_value(str(zoom_percentage))
        return self

    def select_content_and_action(self, content_type: str, action: str) -> BasePage:
        """
        From the applications list that handles how downloaded media is used,
        select a content type and action
        """
        menu = self.get_element("actions-menu", labels=[content_type])
        items = menu.find_elements(By.TAG_NAME, "menuitem")
        target_index = next(
            (
                i
                for i, item in enumerate(items)
                if item.get_attribute("label") == action
            ),
            None,
        )
        if target_index is None:
            raise ValueError(
                f"Option '{action}' not found in actions menu for {content_type}"
            )
        self.click_on("actions-menu", labels=[content_type])
        self.wait.until(
            lambda _: menu.get_attribute("open") is not None
        )  # wait for popup
        menu.send_keys(Keys.HOME)
        for _ in range(target_index):
            menu.send_keys(Keys.DOWN)
        menu.send_keys(Keys.ENTER)
        self.wait.until(
            lambda _: menu.get_attribute("label") == action
        )  # verify selection
        return self

    def select_trackers_to_block(self, *options):
        """Select the trackers to block in the about:preferences page. Unchecks all first."""
        self.elements |= {
            "checkbox-by-label": {
                "selectorData": "checkbox[label='{}']",
                "strategy": "css",
                "groups": ["doNotCache"],
            }
        }
        self.click_on("custom-radio")
        checkboxes = self.get_element("custom-tracker-options-parent").find_elements(
            By.TAG_NAME, "checkbox"
        )
        for checkbox in checkboxes:
            if checkbox.is_selected():
                checkbox.click()
        for option in options:
            self.click_on(option)
            tag = self.get_element(option).tag_name
            if tag == "checkbox":
                self.element_has_attribute(option, "checked")
            elif tag == "menuitem":
                self.element_attribute_is(option, "selected", "true")

        sleep(0.25)
        return self

    def get_history_menulist(self) -> WebElement:
        """
        Gets the web element for the list of history items that appear in about:preferences
        """
        return self.get_element("history_menulist")

    def set_history_option(self, option: str):
        """
        Set the history option in about:preferences.
        """
        history_menulist = self.get_history_menulist()
        self.driver.execute_script("arguments[0].scrollIntoView();", history_menulist)
        sleep(1)
        menulist_popup = Select(self.get_element("history-option-select"))
        menulist_popup.select_by_value(option)
        return self

    # ---- Payment and Address Management ---------------------------------------------------------
    def verify_cc_json(
        self, cc_info_json: dict, credit_card_fill_obj: CreditCardBase
    ) -> BasePage:
        """
        Does the assertions that ensure all the extracted information (the cc_info_json) is the same
        as the generated fake credit_card_fill_obj data.

        ...

        Attributes
        ----------
        cc_info_json: dict
            JSON representation of the extracted information from a web page
        credit_card_fill_obj: CreditCardBase
            The object that contains all the generated information
        """
        assert cc_info_json["cardNumber"][-4:] == credit_card_fill_obj.card_number[-4:]
        _, year = cc_info_json["expDate"].split("/")
        # Compare two digit year to four-digit
        assert int(year) == int(credit_card_fill_obj.expiration_year) + 2000
        return self

    def verify_cc_edit_saved_payments_profile(
        self, credit_card_fill_obj: CreditCardBase
    ):
        """
        Verify saved payment profile data is the same as generated fake credit_card_fill_obj data.
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

        # Press tab again to navigate to the next field (this accounts for the second tab
        # after the name field)
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
        # TODO: update tests in tests/form_autofill to follow this pattern
        self.click_on("add-payment")
        self.switch_to_iframe(1)
        self.fill_and_save_cc_panel_information(cc_data)
        self.switch_to_default_frame()
        return self

    def close_dialog_box(self):
        """Close dialog box for saved addresses or payments."""
        self.element_clickable("panel-popup-button", labels=["close-button"])
        self.click_on("panel-popup-button", labels=["close-button"])
        if self.get_element(
            "panel-popup-button", labels=["close-button"]
        ).is_displayed():
            self.click_on("panel-popup-button", labels=["close-button"])
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
        self.switch_to_iframe_context(self.get_element("browser-popup"))
        if field_name not in fields.keys():
            raise ValueError(
                f"{field_name} is not a valid field name for the cc dialog form."
            )
        value_field = self.find_element(By.ID, fields[field_name])
        if value.isdigit():
            value = int(value)
        if field_name == "expiration_year":
            if int(value) < 100:  # new exp years are all 4-digit
                value = int(value) + 2000
            value_field.click()
            option = next(
                el
                for el in value_field.find_elements(By.TAG_NAME, "option")
                if el.text == str(value)
            )
            option.click()

        elif value_field.tag_name == "select":
            Select(value_field).select_by_index(value)
        else:
            value_field.clear()
            value_field.send_keys(value)
        self.get_element("save-button").click()
        return self

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

        self.click_on("add-address")
        self.switch_to_iframe(1)
        self.fill_and_save_address_panel_information(address_data)
        self.switch_to_default_frame()
        return self

    def select_saved_address_entry(self, idx=0):
        """
        Select one of the entries in the saved addresses list.
        """
        self.switch_to_saved_addresses_popup_iframe()
        select_el = Select(self.get_element("address-saved-options"))
        self.double_click(select_el.options[idx])
        return self

    def _get_tile_data(self, tile_type: str, idx=0) -> dict:
        """Get data-l10n-args from a saved tile"""
        self.element_visible(f"saved-{tile_type}-entry")
        raw_json = self.get_elements(f"saved-{tile_type}-entry")[idx].get_attribute(
            "data-l10n-args"
        )
        return json.loads(raw_json)

    def get_data_from_saved_address(self, idx=0) -> dict:
        """Get data-l10n-args from the saved address card"""
        return self._get_tile_data("address", idx)

    def get_data_from_saved_payment(self, idx=0) -> dict:
        """Get data-l10n-args from the saved payment card"""
        return self._get_tile_data("payment", idx)

    def _edit_tile(self, tile_type: str, idx=0):
        """Open the edit view of payment or address"""
        tiles = self.get_elements(f"edit-{tile_type}")
        tiles[idx].click()

    def edit_address(self, idx=0):
        """Click the edit button on a given address"""
        self._edit_tile("address", idx)

    def edit_payment(self, idx=0):
        """Click the edit button on a given payment"""
        self._edit_tile("payment", idx)

    def _get_autofill_profiles(self, tile_type: str) -> List[WebElement]:
        """Gets any type of autofill profile, do not use against n=0"""
        self.element_visible(f"saved-{tile_type}-entry")
        return self.get_elements(f"saved-{tile_type}-entry")

    def get_all_saved_cc_profiles(self) -> List[WebElement]:
        """Gets the saved credit card profiles in the cc panel"""
        return self._get_autofill_profiles("payment")

    def get_all_saved_address_profiles(self) -> List[WebElement]:
        """Gets the saved credit card profiles in the cc panel"""
        return self._get_autofill_profiles("address")

    def _confirm_n_profiles(self, tile_type: str, n: int) -> BasePage:
        """Confirm that _n_ profiles of a type exist, where n>0"""
        self.expect(lambda _: len(self._get_autofill_profiles(tile_type)) == n)
        return self

    def confirm_n_addresses(self, n: int) -> BasePage:
        """Confirm that _n_ addresses exist where n>0"""
        return self._confirm_n_profiles("address", n)

    def confirm_n_payments(self, n: int) -> BasePage:
        """Confirm that _n_ payments exist where n>0"""
        return self._confirm_n_profiles("payment", n)

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
        self.click_on("saved-payments-button")
        iframe = self.get_element("browser-popup")
        return iframe

    def switch_to_edit_saved_payments_popup_iframe(self) -> BasePage:
        """
        Switch to form iframe to edit saved payments.
        """
        self.switch_to_default_frame()
        self.switch_to_iframe_context(self.get_element("browser-popup"))
        return self

    def press_button_get_popup_dialog_iframe(self, button_label: str) -> WebElement:
        """
        Returns the iframe object for the dialog panel in the popup after pressing some button that
        triggers a popup
        """
        # hack to know if the current iframe is the default browser one or not
        if self.get_iframe().location["x"] > 0:
            self.click_on("close-dialog")
        self.click_on("prefs-button", labels=[button_label])
        iframe = self.get_element("browser-popup")
        return iframe

    def clear_cookies_and_get_dialog_iframe(self):
        """
        Returns the iframe object for the dialog panel in the popup after pressing the clear site
        data button.
        """
        self.scroll_to_element("clear-site-data-button")
        self.click_on("clear-site-data-button")
        return self.get_element("browser-popup")

    def get_saved_addresses_popup_iframe(self) -> WebElement:
        """
        Returns the iframe object for the dialog panel in the popup
        """
        self.click_on("saved-addresses-button")
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

    def get_and_switch_iframe(self):
        """
        Gets the webelement for the iframe that commonly appears in about:preferences and switches
        to it.
        """
        iframe = self.get_iframe()
        self.switch_to_iframe_context(iframe)
        return self

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
        Takes the sample AutofillAddressBase object and fills it into the popup panel in the
        about:prefs section
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

    def get_cookie_site_data_value(self) -> int | None:
        """
        With the 'Clear browsing data and cookies' popup open,
        returns the <memory used> value of the option for 'Cookies and site data (<memory used>)'.
        The <memory used> value for no cookies is '0 bytes', otherwise values are
        '### MB', or '### KB'
        """
        # Find the dialog option elements containing the checkbox label
        self.element_exists("clear-data-dialog-options")
        cookies_checkbox = self.get_element("cookies-data-checkbox")
        self.element_has_attribute(cookies_checkbox, "data-l10n-args")
        cookies_object = cookies_checkbox.get_attribute("data-l10n-args")
        # dictionary holding the cookies amount and unit
        # {amount: "1234", unit: "MB"}
        cookies_amount = json.loads(cookies_object)
        return int(cookies_amount.get("amount"))

    def get_manage_data_site_element(self, site: str) -> WebElement:
        """
        Returns the WebElement for the given site in the manage site data popup
        """
        element = self.get_element("manage-cookies-site", labels=[site])
        return element

    def remove_cookie_site_data(self, cookie_site: str = "", all_sites: bool = False):
        """
        Removes a given site from the manage site data popup
        If all_sites is True, removes all sites from the manage site data popup and check that
        "cookies-manage-data-sitelist" only has one row.
        """
        sites = self.get_elements("children-host-elements")
        if all_sites:
            self.click_on("remove-all-button")
            self.element_exists("cookies-manage-data-sitelist")
            sites = self.get_elements("children-host-elements")
            self.expect(lambda _: len(sites) == 0)
        else:
            cookie_item = self.get_manage_data_site_element(cookie_site)
            cookie_item.click()
            self.click_on("remove-selected-cookie-button")
            new_sites = self.get_elements("children-host-elements")
            self.expect(lambda _: len(new_sites) == len(sites) - 1)

    def open_autoplay_modal(self) -> BasePage:
        """
        Opens the Autoplay settings modal dialog from the about:preferences#permissionsData page.
        """
        self.open()
        self.element_visible("autoplay-settings-button")
        self.click_on("autoplay-settings-button")
        self.driver.switch_to.frame(self.get_iframe())
        self.click_on("autoplay-settings")
        return self

    def set_autoplay_setting_in_preferences(
        self,
        settings: Literal["allow-audio-video", "block-audio-video", "allow-audio-only"],
    ) -> BasePage:
        """
        Open the Autoplay settings panel and choose a setting for all sites.
        Arguments:
            settings: "allow-audio-video" → Allow Audio and Video, "block-audio-video" →
            Block Audio and Video, "allow-audio-only" → Allow Audio but block Video
        """
        self.open_autoplay_modal()
        self.click_on(settings)
        self.click_on("spacer")
        self.click_on("autoplay-save-changes")
        return self

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
            lambda _: (
                self.get_element("migration-progress-header").text
                in ["Data imported successfully", "Data import complete"]
            )
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

    @BasePage.context_content
    def get_app_name_for_mime_type(self, mime_type: str) -> str:
        """
        Return the application name associated with a given MIME type in about:preferences.
        Argument:
            mime_type: the MIME type to look up (e.g., "application/msword").
        """
        # Locate the row for the given MIME type
        mime_type_item = self.get_element("mime-type-item", labels=[mime_type])

        # Find the description element that contains application info
        action_description = self.get_element(
            "mime-type-item-description", parent_element=mime_type_item
        )

        # Parse the JSON data-l10n-args attribute and extract app name
        mime_type_data = json.loads(action_description.get_attribute("data-l10n-args"))
        return mime_type_data["app-name"]

    def set_pdf_handling_to_always_ask(self) -> BasePage:
        """
        Set PDF content type handling to "Always ask" in Applications settings.
        """
        self.click_on("pdf-content-type")
        self.click_on("pdf-actions-menu")
        menu = self.get_element("pdf-actions-menu")
        menu.send_keys(Keys.DOWN)
        menu.send_keys(Keys.ENTER)
        return self

    @BasePage.context_chrome
    def handle_unknown_content_dialog(self) -> BasePage:
        """
        Wait for the unknown content type dialog to appear and close it with Escape.
        """
        self.wait.until(lambda _: len(self.driver.window_handles) > 1)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.wait.until(lambda _: self.get_element("unknown-content-type-dialog"))

        # Close the dialog with Escape
        dialog = self.get_element("unknown-content-type-dialog")
        dialog.send_keys(Keys.ESCAPE)
        return self

    def open_manage_cookies_data_dialog(self) -> BasePage:
        """
        Open the 'Manage Cookies and Site Data' dialog safely.

        Waits for the 'Manage browsing data' button to be clickable, clicks it to open
        the dialog, and switches the driver context to the dialog's iframe. After
        calling this method, subsequent element interactions will be within the
        dialog's iframe context.

        Note: This method assumes the about:preferences page is already open.
        Call self.open() first if needed.
        """
        self.element_clickable("prefs-button", labels=["Manage browsing data"])
        manage_data_popup = self.press_button_get_popup_dialog_iframe(
            "Manage browsing data"
        )
        BrowserActions(self.driver).switch_to_iframe_context(manage_data_popup)
        return self

    def uncheck_history_suggestion(self):
        """
        Uncheck the 'historySuggestion' checkbox if it's currently checked.
        """
        checkbox = self.get_element("history-suggestion")
        if checkbox.is_selected():
            checkbox.click()

    def verify_element_is_interactable(
        self, locator: str, text_value: str = None
    ) -> BasePage:
        """Verify that the element with the given locator is interactable."""
        element = self.get_element(locator)
        if element.is_displayed():
            self.scroll_to_element(locator)
            self.element_clickable(locator)
            if text_value:
                self.element_has_text(locator, text_value)
        return self

    def open_clear_cookie_site_and_get_data(self):
        """
        Open about:preferences#privacy, show the 'Clear Data' dialog, switch into its iframe,
        wait for its option container to be present, read the value, then switch back.
        """
        self.open()
        iframe = self.clear_cookies_and_get_dialog_iframe()
        self.switch_to_iframe_context(iframe)
        val = self.get_cookie_site_data_value()
        self.switch_to_default_frame()
        self.close_dialog_box()
        return val

    def open_clear_cookie_site_and_clear_data(self):
        """
        Open about:preferences#privacy and clear cookies and site data.
        """
        iframe = self.clear_cookies_and_get_dialog_iframe()
        self.switch_to_iframe_context(iframe)
        self.click_on("clear-data-accept-button")
        self.switch_to_default_frame()

    def enable_show_sidebar(self):
        """Enable the Show Sidebar checkbox under General > Browser Layout if not already checked"""
        if not self.get_element("show-sidebar-checkbox").get_attribute("checked"):
            self.click_on("show-sidebar-shadow-box")
        self.element_has_attribute("show-sidebar-checkbox", "checked")
        return self

    def wait_for_default_search_engine(self, engine_name: str) -> BasePage:
        """Wait until the UI reflects the selected default search engine."""
        self.wait.until(
            lambda _: self.element_has_text("select-wrapper-button", engine_name)
        )
        return self

    def open_primary_password_popup(self, browser_actions):
        """
        Opens the 'Change Primary Password' popup by checking the checkbox
        and switches to the iframe context.
        """
        self.click_on("use-primary-password")
        popup = self.get_element("browser-popup")
        browser_actions.switch_to_iframe_context(popup)
        return self

    def set_primary_password(self, password):
        """
        Sets a new primary password.
        """
        self.get_element("enter-new-password").send_keys(password)
        self.get_element("reenter-new-password").send_keys(password)
        self.click_on("submit-password")
        return self

    def accept_alert_and_verify_text(self, expected_text: str):
        """
        Verifies alert text and accepts it.
        """
        alert = self.get_alert()
        assert expected_text in alert.text
        alert.accept()
        return self

    def create_primary_password(self, password: str, alert_text: str, ba):
        """Creates a Primary Password, confirms alert"""
        self.open()
        self.open_primary_password_popup(ba)
        self.set_primary_password(password)
        self.accept_alert_and_verify_text(alert_text)
        return self

    # ── AI Controls ──────────────────────────────────────────────────────

    def toggle_ai_killswitch_click(self) -> BasePage:
        """
        Click the AI killswitch toggle. When transitioning from unblocked to
        blocked, a confirmation dialog appears; click its "Block" button to
        confirm. The dialog is not shown when re-enabling AI.
        """
        confirm_required = (
            self.get_element("ai-controls-toggle").get_attribute("aria-pressed")
            == "false"
        )
        self.click_on("ai-controls-toggle")
        if confirm_required:
            self.element_visible("ai-controls-disable-dialog-button")
            buttons = self.get_elements("ai-controls-disable-dialog-button")
            block = [el for el in buttons if el.get_attribute("label") == "Block"][0]
            block.click()
        return self

    def expect_ai_killswitch_state(self, pressed=False) -> BasePage:
        """
        Wait for AI killswitch to match expected state
        """
        self.element_attribute_is(
            "ai-controls-toggle", "aria-pressed", str(pressed).lower()
        )
        return self

    def expect_ai_selects_state(self, disabled=False) -> BasePage:
        """
        Wait for AI feature selects to match expected state
        """
        for key in [
            "ai-control-translations-select",
            "ai-control-sidebar-chatbot-select",
        ]:
            if disabled:
                self.element_has_attribute(key, "disabled")
            else:
                self.element_attribute_is_not(key, "disabled", "")
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
        self.element_clickable("sidebar-options", labels=[option])
        self.click_on("sidebar-options", labels=[option])

    def get_language_addon_list(self):
        """Gets the cards from the about:addons page"""
        addon_list_parent = self.get_element("languages-addon-list")
        return self.get_element(
            "languages-addon-list-card", multiple=True, parent_element=addon_list_parent
        )

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
