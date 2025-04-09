import json
import logging
from html import unescape
from typing import List, Optional

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object_autofill_popup import AutofillPopup
from modules.classes.autofill_base import AutofillAddressBase
from modules.classes.credit_card import CreditCardBase
from modules.page_base import BasePage
from modules.util import BrowserActions, Utilities


class Autofill(BasePage):
    """
    Page Object Model for auto site (https://mozilla.github.io/form-fill-examples/) base parent object of all
    autofill page related objects
    """

    field_mapping = {}  # Default; subclasses will override

    URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/"

    def __init__(self, driver: Firefox, **kwargs):
        super().__init__(driver, **kwargs)
        self.driver = driver
        self.ba = BrowserActions(self.driver)
        self.util = Utilities()
        self.autofill_popup = AutofillPopup(self.driver)

    def _fill_input_element(self, field_name: str, term: str):
        """
        Given BrowserActions object, the string of the element to be identified and the string term to be sent to the
        input, identify the webelement and send the term to the input field without any additional keystrokes.

        Arguments:
            field_name : The name of the input field to be identified
            term: The string to be sent to the input field
        """
        form_field_element = self.get_element("form-field", labels=[field_name])
        self.ba.clear_and_fill(form_field_element, term, press_enter=False)

    def _click_form_button(self, field_name):
        """Clicks submit on the form"""
        self.click_on("submit-button", labels=[field_name])

    def fill_and_submit(self, data_object: CreditCardBase | AutofillAddressBase):
        """Fill and submit from data object.

        Arguments:
            data_object: object containing autofill data.
        """
        for field_name, attr_name in self.field_mapping.items():
            value = getattr(data_object, attr_name, None)
            if value is not None:
                self._fill_input_element(field_name, value)
        self._click_form_button("submit")

    def verify_field_autofill_dropdown(
        self,
        fields_to_test: List[str],
        excluded_fields: Optional[List[str]] = None,
        region: Optional[str] = None,
    ):
        """
        A common method to check which fields trigger the autofill dropdown. This is used in both CC and Address pages.
        - fields_to_test: The primary list of fields for this page (cc fields, address fields).
        - excluded_fields: Fields that should NOT trigger an autofill dropdown.
        - region: If provided, handle region-specific behavior (e.g., skip address-level1 for DE/FR).
        """
        # Create a copy of fields_to_test to avoid modifying the original
        fields_to_check = fields_to_test[:]

        # Handle region-specific behavior
        if region in ["DE", "FR"] and "address-level1" in fields_to_check:
            fields_to_check.remove("address-level1")

        # Check fields that SHOULD trigger the autofill dropdown
        for field_name in fields_to_check:
            self.double_click("form-field", labels=[field_name])
            self.autofill_popup.ensure_autofill_dropdown_visible()
            logging.info(f"Autofill dropdown appears for field '{field_name}'.")

        # Check fields that should NOT trigger the autofill dropdown
        if excluded_fields:
            for field_name in excluded_fields:
                self.double_click("form-field", labels=[field_name])
                self.autofill_popup.ensure_autofill_dropdown_not_visible()
                logging.info(
                    f"No autofill dropdown appears for field '{field_name}', as expected."
                )

        return self

    def verify_field_highlight(
        self,
        fields_to_test: List[str],
        expected_highlighted_fields: Optional[List[str]] = None,
        extra_fields: Optional[List[str]] = None,
    ):
        """
        A common method to check which fields have the "yellow highlight". This is used in both CC and Address pages.
        - fields_to_test: The primary list of fields for this page (cc fields, address fields).
        - expected_highlighted_fields: Which ones are expected to be highlighted. Defaults to all in `fields_to_test`.
        - extra_fields: If some pages have extra fields to test (e.g. 'cc-csc'), pass them here.
        """

        if expected_highlighted_fields is None:
            # By default, everything in fields_to_test is expected to be highlighted
            expected_highlighted_fields = fields_to_test[:]

        if extra_fields:
            fields_to_actually_check = fields_to_test + extra_fields
        else:
            fields_to_actually_check = fields_to_test

        is_yellow_highlight = lambda rgb: (
            rgb[0] >= 250 and rgb[1] >= 250 and 180 < rgb[2] < 220
        )

        for field_name in fields_to_actually_check:
            # Focus the field so the highlight is visible
            self.click_on("form-field", labels=[field_name])

            # Get all colors in the field
            selector = self.get_selector("form-field", labels=[field_name])
            colors = self.ba.get_all_colors_in_element(selector)
            logging.info(f"Colors found in '{field_name}': {colors}")

            # Check the highlight
            is_field_highlighted = any(is_yellow_highlight(color) for color in colors)
            should_be_highlighted = field_name in expected_highlighted_fields

            # Assert based on expectation
            if should_be_highlighted:
                assert is_field_highlighted, (
                    f"Expected yellow highlight on '{field_name}', but none found."
                )
                logging.info(f"Yellow highlight found in '{field_name}'.")
            else:
                assert not is_field_highlighted, (
                    f"Expected NO yellow highlight on '{field_name}', but found one."
                )
                logging.info(f"No yellow highlight in '{field_name}', as expected.")

        return self

    def select_autofill_option(self, field, index: int = 1):
        """
        Presses the autofill panel that pops up after you double-click an input field

        Argument:
            autofill_popup: AutofillPopup
            field:  field to click to show autofill option.
            index: which autofill option to pick.
        """
        self.double_click("form-field", labels=[field])
        self.autofill_popup.ensure_autofill_dropdown_visible()
        self.autofill_popup.select_nth_element(index)
        return self


class AddressFill(Autofill):
    """
    Page Object Model for auto site (https://mozilla.github.io/form-fill-examples/basic.html)
    """

    URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/basic.html"

    fields = [
        "name",
        "organization",
        "street-address",
        "address-level2",  # city
        "address-level1",  # state/province
        "postal-code",
        "country",
        "email",
        "tel",
    ]

    field_mapping = {
        "name": "name",
        "organization": "organization",
        "street-address": "street_address",
        "address-level2": "address_level_2",
        "address-level1": "address_level_1",
        "postal-code": "postal_code",
        "country": "country_code",
        "email": "email",
        "tel": "telephone",
    }

    def __init__(self, driver: Firefox, **kwargs):
        super().__init__(driver, **kwargs)

    @BasePage.context_chrome
    def verify_autofill_displayed(self):
        """
        Verifies that the autofill suggestions are displayed.
        """
        element = self.get_element("select-address")
        self.expect(EC.visibility_of(element))

    def check_autofill_preview_for_field(
        self,
        field_label: str,
        address_sample_data: AutofillAddressBase,
        region: str = None,
    ):
        """
        Check that hovering over a field autofill option will prefill the other fields.

        Arguments:
            field_label: str,
            address_sample_data: address autofill sample data,
            region: country code in use
        """
        # Skip fields that don't appear in the dropdown for certain regions.
        if field_label == "address-level1" and region in ["DE", "FR"]:
            return
        self.double_click("form-field", labels=[field_label])
        self.autofill_popup.ensure_autofill_dropdown_visible()
        self.autofill_popup.hover("select-form-option")
        self.verify_autofill_data_on_hover(address_sample_data)

    def send_keys_to_element(self, name: str, label: str, keys: str):
        """
        Send keys to the specified element.
        """
        elem = self.get_element(name, labels=[label])
        current_value = elem.get_attribute("value")
        new_value = current_value + keys
        elem.clear()
        elem.send_keys(new_value)

    def verify_autofill_data(self, autofill_data: AutofillAddressBase):
        """
        Verifies that the autofill data matches the expected values.

        Arguments:
            autofill_data: AutofillAddressBase object containing expected data.
        """
        field_mapping = {
            "Name": "name-field",
            "Organization": "org-field",
            "Street Address": "street-field",
            "City": "add-level2-field",
            "State": "add-level1-field",
            "ZIP Code": "zip-field",
            "Country": "country-field",
            "Email": "email-field",
            "Phone": "phone-field",
        }

        # Get actual values from web elements
        actual_values = {
            field: self.get_element(locator).get_attribute("value")
            for field, locator in field_mapping.items()
        }

        # Get expected values from autofill data
        expected_values = {
            "Name": autofill_data.name,
            "Organization": autofill_data.organization,
            "Street Address": autofill_data.street_address,
            "City": autofill_data.address_level_2,
            "State": autofill_data.address_level_1,
            "ZIP Code": autofill_data.postal_code,
            "Country": autofill_data.country_code,
            "Email": autofill_data.email,
            "Phone": self.util.normalize_regional_phone_numbers(
                autofill_data.telephone, autofill_data.country_code
            ),
        }

        self.verify_data(actual_values, expected_values)

    @BasePage.context_chrome
    def verify_autofill_data_on_hover(self, autofill_data: AutofillAddressBase):
        """
        Verifies that the autofill preview data matches the expected values when hovering

        Arguments:
            autofill_data: AutofillAddressBase object containing expected data.
        """

        # get preview data from hovering through the chrome context
        element = self.autofill_popup.get_element("address-preview-form-container")
        # get every span element that is a child of the form and is not empty
        children = [
            x.get_attribute("innerHTML")
            for x in element.find_elements(By.TAG_NAME, "span")
            if len(x.get_attribute("innerHTML").strip()) >= 2
        ]

        # normalize phone number data
        autofill_data.telephone = self.util.normalize_regional_phone_numbers(
            autofill_data.telephone, autofill_data.country_code
        )
        for expected in children:
            if expected[0] == "+":
                expected = self.util.normalize_phone_number(expected)
            if len(expected) == 2 and expected != autofill_data.country_code:
                continue
            assert unescape(expected) in autofill_data.__dict__.values(), (
                f"Mismatched data: {expected} not in {autofill_data}."
            )

    def verify_data(self, actual_values, expected_values):
        """Verify data between actual and expected values"""
        # Validate each field
        for field, expected in expected_values.items():
            actual = actual_values[field]

            # Skip State verification for DE and FR
            if field == "State" and expected_values["Country"] in ["DE", "FR"]:
                continue

            # Normalize phone numbers before comparison
            if field == "Phone":
                actual = self.util.normalize_phone_number(actual)

            assert actual == expected, (
                f"Mismatch in {field}: Expected '{expected}', but got '{actual}'"
            )

    def verify_field_yellow_highlights(
        self, region=None, fields_to_test=None, expected_highlighted_fields=None
    ):
        if fields_to_test is None:
            fields_to_test = self.fields  # By default, test all address fields

        # Skip 'address-level1' if region is DE or FR
        if region in ["DE", "FR"] and "address-level1" in fields_to_test:
            fields_to_test.remove("address-level1")

        return self.verify_field_highlight(
            fields_to_test=fields_to_test,
            expected_highlighted_fields=expected_highlighted_fields,
        )

    def verify_autofill_dropdown_addresses(self, region=None, fields_to_test=None):
        """Verifies autofill dropdown for address fields."""
        if fields_to_test is None:
            fields_to_test = self.fields

        return self.verify_field_autofill_dropdown(
            fields_to_test=fields_to_test, region=region
        )

    def fill_and_save(
        self, region: str = "US", door_hanger: bool = True
    ) -> AutofillAddressBase:
        """
        Fills an address form with randomly generated data and interacts with the autofill popup.

        Arguments:
            region: Country code in use
            door_hanger: check to click save on door hanger
        """
        fake_address_autofill_data = self.util.fake_autofill_data(region)
        self.fill_and_submit(fake_address_autofill_data)
        if door_hanger:
            self.autofill_popup.click_doorhanger_button("save")
        return fake_address_autofill_data

    def autofill_and_verify(
        self, field_label: str, address_autofill_data: AutofillAddressBase
    ):
        """
        Autofills a form field, verifies the data, and clears it if necessary.

        Arguments:
            field_label : The label of the field being autofilled.
            address_autofill_data : The generated autofill data for verification.
        """
        # Skip address-level1 (State) selection for DE and FR
        if field_label == "address-level1" and address_autofill_data.country_code in [
            "DE",
            "FR",
        ]:
            return

        # Double-click a field and choose the first element from the autocomplete dropdown
        self.double_click("form-field", labels=[field_label])
        self.autofill_popup.ensure_autofill_dropdown_visible()
        self.autofill_popup.select_nth_element(1)

        # Verify autofill data
        self.verify_autofill_data(address_autofill_data)

        # Clear form autofill
        self.double_click("form-field", labels=[field_label])
        self.autofill_popup.ensure_autofill_dropdown_visible()
        self.autofill_popup.click_clear_form_option()

    def verify_all_fields_cleared(self):
        """
        Verifies that all autofill fields are empty.
        """
        field_mapping = {
            "Name": "name-field",
            "Organization": "org-field",
            "Street Address": "street-field",
            "City": "add-level2-field",
            "State": "add-level1-field",
            "ZIP Code": "zip-field",
            "Country": "country-field",
            "Email": "email-field",
            "Phone": "phone-field",
        }

        # Get actual values from web elements
        actual_values = {
            field: self.get_element(locator).get_attribute("value")
            for field, locator in field_mapping.items()
        }

        # Validate each field is empty
        for field, value in actual_values.items():
            assert not value, f"Field '{field}' is not empty: Found '{value}'"

    def clear_and_verify(
        self, field_label: str, address_autofill_data: AutofillAddressBase
    ):
        """
        Autofills a form field, clears it, and verifies that it is empty.

        Arguments:
            field_label : The label of the field being autofilled.
            address_autofill_data : The generated autofill data for verification.
        """
        # Skip address-level1 (State) selection for DE and FR
        if field_label == "address-level1" and address_autofill_data.country_code in [
            "DE",
            "FR",
        ]:
            return

        # Double-click a field and choose the first element from the autocomplete dropdown
        self.double_click("form-field", labels=[field_label])
        self.autofill_popup.ensure_autofill_dropdown_visible()
        self.autofill_popup.select_nth_element(1)

        # Clear form autofill
        self.double_click("form-field", labels=[field_label])
        self.autofill_popup.ensure_autofill_dropdown_visible()
        self.autofill_popup.click_clear_form_option()

        # Verify all fields are cleared
        self.verify_all_fields_cleared()


class CreditCardFill(Autofill):
    """
    Page Object Model for auto site (https://mozilla.github.io/form-fill-examples/basic_cc.html)
    """

    URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/basic_cc.html"
    fields = ["cc-name", "cc-number", "cc-exp-month", "cc-exp-year"]
    field_mapping = {
        "cc-name": "name",
        "cc-number": "card_number",
        "cc-exp-month": "expiration_month",
        "cc-exp-year": "expiration_year",
        "cc-csc": "cvv",
    }

    def __init__(self, driver: Firefox, **kwargs):
        super().__init__(driver, **kwargs)

    def verify_autofill_dropdown_credit_card(self):
        """Verifies autofill dropdown for credit card fields."""
        return self.verify_field_autofill_dropdown(
            fields_to_test=self.fields, excluded_fields=["cc-csc"]
        )

    def verify_credit_card_form_data(
        self, credit_card_sample_data: CreditCardBase
    ) -> Autofill:
        """
        Verifies that the information is filled correctly.

        Attributes
        ----------

        credit_card_sample_data: CreditCardBase
            The object that contains all the relevant information about the credit card autofill
        """
        info_list = self.extract_credit_card_obj_into_list(credit_card_sample_data)
        for i in range(len(info_list)):
            self.element_attribute_contains(
                "form-field", "value", info_list[i], labels=[self.fields[i]]
            )
        return self

    def fill_and_save(self, door_hanger: bool = True) -> CreditCardBase:
        """
        Fills a credit card form with randomly generated data and interacts with the autofill popup.

        ...

        Arguments:
            door_hanger: check to click save on door hanger
        """
        credit_card_sample_data = self.util.fake_credit_card_data()
        self.fill_and_submit(credit_card_sample_data)
        if door_hanger:
            self.autofill_popup.click_doorhanger_button("save")
        return credit_card_sample_data

    def update_field(self, field: str, field_data: str):
        """
        Updates a field in the form with given data.

        ...

        Parameters
        ----------

        field: str
            The name of the field to fill

        field_data: str
            The data to put in the field
        """
        self._fill_input_element(field, field_data)
        self._click_form_button("submit")

    def update_credit_card_information(
        self, field_name: str, field_data: str, save_card=False
    ):
        """
        Updates the credit card based on field that is to be changed by first autofilling everything then updating
        the field of choice then pressing submit and handling the popup.
        """
        self.update_field(field_name, field_data)
        self._click_form_button("submit")

        if save_card or field_name == "cc-number":
            self.autofill_popup.click_on("doorhanger-save-button")
        else:
            self.autofill_popup.click_on("update-card-info-popup-button")

    @BasePage.context_chrome
    def verify_autofill_cc_data_on_hover(self, autofill_data: CreditCardBase):
        """
        Verifies that the credit card autofill preview data matches the expected values when hovering

        Arguments:
            autofill_data: CreditCardBase object containing expected credit card data.
        """
        # Get preview data from hovering through the chrome context
        try:
            # Attempt to parse the string as JSON
            container = json.loads(
                self.autofill_popup.get_element(
                    "cc-preview-form-container"
                ).get_attribute("ac-comment")
            )
        except json.JSONDecodeError:
            # If parsing fails, raise ValueError.
            raise ValueError("Given preview data is incomplete.")
        container_data = container.get("fillMessageData", {}).get("profile", {})
        assert container_data, "No preview data available."
        assert all(field in container_data.keys() for field in self.fields), (
            "Not all fields present in preview data."
        )

        # sanitize data
        autofill_data.card_number = autofill_data.card_number[-4:]
        expected_values = [
            int(val) if val.isnumeric() else val
            for val in autofill_data.__dict__.values()
        ]
        for field, value in container_data.items():
            if field in self.fields:
                value = str(value)
                if field == "cc-number":
                    value = value[-4:]
                elif field == "cc-exp-year":
                    value = value[-2:]
                value = int(value) if value.isnumeric() else value
                # Check if this value exists in our CreditCardBase object
                assert value in expected_values, (
                    f"Mismatched data: {(field, value)} not in {expected_values}."
                )

    @staticmethod
    def extract_credit_card_obj_into_list(
        credit_card_sample_data: CreditCardBase,
    ) -> List[str]:
        """
        Extracts the credit card information from the object and returns it as a list.

        Attributes
        ----------
        credit_card_sample_data: CreditCardBase
            The credit card information object
        """
        ret_val = [
            credit_card_sample_data.name,
            credit_card_sample_data.card_number,
            credit_card_sample_data.expiration_month,
            f"20{credit_card_sample_data.expiration_year}",
        ]
        return ret_val

    def verify_updated_information(
        self, credit_card_sample_data: CreditCardBase, field_name: str, new_data: str
    ) -> Autofill:
        """
        Verifies that there is only 1 profile in the popup panel, updates the credit card information and verifies all
        the fields according to the passed in credit card information object

        Attributes
        ----------

        credit_card_sample_data: CreditCardBase
            An instance of the fake generated data

        field_name: str
            The name of the field to update

        new_data: str
            The data to update the field with
        """

        # updating the profile accordingly
        self.update_credit_card_information(field_name, new_data)

        # autofill data
        self.select_autofill_option(field_name)

        # verifying the correct data
        self.verify_credit_card_form_data(credit_card_sample_data)
        return self

    def check_cc_autofill_preview_for_field(
        self, field_label: str, credit_card_sample_data: CreditCardBase
    ):
        """
        Check that hovering over a field autofill option will prefill the other fields.

        Arguments:
            field_label: str,
            credit_card_sample_data: credit card autofill sample data,
        """
        self.double_click("form-field", labels=[field_label])
        self.autofill_popup.ensure_autofill_dropdown_visible()
        self.autofill_popup.hover("select-form-option")
        self.verify_autofill_cc_data_on_hover(credit_card_sample_data)

    def update_cc(
        self, credit_card_sample_data: CreditCardBase, field: str
    ) -> Autofill:
        """
        Generates a new data for credit card according to field given, updates the credit card information in the form.
        """
        cc_mapping = {
            "cc-name": "name",
            "cc-exp-month": "expiration_month",
            "cc-exp-year": "expiration_year",
            "cc-number": "card_number",
        }

        new_cc_data = getattr(self.util.fake_credit_card_data(), cc_mapping[field])
        while new_cc_data == getattr(credit_card_sample_data, cc_mapping[field]):
            new_cc_data = getattr(self.util.fake_credit_card_data(), cc_mapping[field])

        setattr(credit_card_sample_data, cc_mapping[field], new_cc_data)

        self.verify_updated_information(credit_card_sample_data, field, new_cc_data)
        return self

    def verify_clear_form_all_fields(self):
        """
        Clears all fields in the form by triggering the clear action from each field in turn. After each clear
        action, verifies that all fields are empty, regardless of which field initiated the clear.
        """
        for field in self.fields:
            self.click_on("form-field", labels=[field])
            self.autofill_popup.click_autofill_form_option()
            self.click_on("form-field", labels=[field])
            self.autofill_popup.click_clear_form_option()
            # Verify that all fields are blank
            for f in self.fields:
                self.element_attribute_contains("form-field", "value", "", labels=[f])
            # Verify that the 'cc-csc' field does not trigger an autofill dropdown
            self.double_click("form-field", labels=["cc-csc"])
            self.autofill_popup.ensure_autofill_dropdown_not_visible()

    def autofill_and_clear_all_fields(self, credit_card_data: CreditCardBase):
        """
        For each field select autofill option and clear.
        """
        for field in self.fields:
            # press autofill panel for a field.
            self.select_autofill_option(field)
            # verify cc data in form.
            self.verify_credit_card_form_data(credit_card_data)
            # Clear the fields after verification
            self.click_on("form-field", labels=[field])
            self.autofill_popup.click_clear_form_option()

    def verify_field_yellow_highlights(self, expected_highlighted_fields=None):
        """
        Reuses the common highlight-check method from the base class.
        We also want to include the "cc-csc" field in the test, so we
        pass it via 'extra_fields'.
        """
        return self.verify_field_highlight(
            fields_to_test=self.fields,
            expected_highlighted_fields=expected_highlighted_fields,
            extra_fields=["cc-csc"],
        )


class LoginAutofill(Autofill):
    """
    Page Object Model for the form autofill demo page with many logins
    """

    URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/password_manager/login_and_pw_change_forms.html"

    class LoginForm:
        """
        Subclass of the Login Autofill Form where you can interact with the Login Form
        """

        def __init__(self, driver: Firefox, parent: "LoginAutofill", **kwargs) -> None:
            super().__init__(driver, **kwargs)
            self.driver = driver
            self.parent = parent
            self.username_field = None
            self.password_field = None
            self.submit_button = None

        def fill_username(self, username: str) -> None:
            """Fill the username field after ensuring it's clickable."""
            self.parent.element_clickable("username-login-field")
            if self.username_field is None:
                self.username_field = self.parent.get_element("username-login-field")
            self.username_field.send_keys(username)

        def fill_password(self, password: str) -> None:
            """Fill the password field after ensuring it's clickable."""
            self.parent.element_clickable("password-login-field")
            if self.password_field is None:
                self.password_field = self.parent.get_element("password-login-field")
            self.password_field.send_keys(password)

        def submit(self) -> None:
            if self.submit_button is None:
                self.submit_button = self.parent.get_element("submit-button-login")
            self.submit_button.click()


class TextAreaFormAutofill(Autofill):
    """
    Page Object Model for the form autofill demo page with a textarea
    """

    URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/textarea_select.html"
