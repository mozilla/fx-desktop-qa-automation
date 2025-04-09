import json
import logging
from html import unescape
from typing import List, Optional

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

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

    # Default; subclasses will override
    field_mapping = {}
    fields = []

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

    def fill_and_submit(self, data_object: CreditCardBase | AutofillAddressBase | dict):
        """Fill and submit from data object or dictionary.

        Arguments:
            data_object: object containing autofill data.
        """
        if not self.field_mapping:
            raise NotImplementedError(
                "Method should only be called in inherited classes."
            )
        for field_name, attr_name in self.field_mapping.items():
            value = (
                getattr(data_object, attr_name, None)
                if not isinstance(data_object, dict)
                else data_object.get(field_name)
            )
            if value is not None:
                self._fill_input_element(field_name, value)
        self._click_form_button("submit")

    def update_form_data(
        self,
        sample_data: AutofillAddressBase | CreditCardBase,
        field: str,
        value: str | int,
    ):
        """
        Update the form field with the new value.

        Arguments:
            sample_data: sample data instance used to verify change.
            field: field being changed.
            value: value being added.
        """
        # updating the profile accordingly
        self.update_and_save(field, value)

        # autofill data
        self.select_autofill_option(field)

        # verifying the correct data
        self.verify_form_data(sample_data)
        return self

    def verify_form_data(self, sample_data: CreditCardBase | AutofillAddressBase):
        """Verify that form is filled correctly against sample data."""
        if not self.field_mapping:
            raise NotImplementedError(
                "Method should only be called in inherited classes."
            )
        for field_name, attr_name in self.field_mapping.items():
            if field_name != "cc-csc":
                expected_value = getattr(sample_data, attr_name, None)
                self.element_attribute_contains(
                    "form-field", "value", expected_value, labels=[field_name]
                )

    def verify_field_autofill_dropdown(
        self,
        fields_to_test: List[str] = None,
        excluded_fields: Optional[List[str]] = None,
        region: Optional[str] = None,
    ):
        """
        A common method to check which fields trigger the autofill dropdown. This is used in both CC and Address pages.

        Arguments:
            fields_to_test: The primary list of fields for this page (cc fields, address fields).
            excluded_fields: Fields that should NOT trigger an autofill dropdown.
            region: If provided, handle region-specific behavior (e.g., skip address-level1 for DE/FR).
        """

        if not self.field_mapping:
            raise NotImplementedError(
                "Method should only be called in inherited classes."
            )

        if fields_to_test is None:
            fields_to_test = self.fields

        # Handle region-specific behavior
        if region in ["DE", "FR"] and "address-level1" in fields_to_test:
            fields_to_test.remove("address-level1")

        # Check fields that SHOULD trigger the autofill dropdown
        for field_name in fields_to_test:
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
        fields_to_test: List[str] = None,
        expected_highlighted_fields: Optional[List[str]] = None,
        extra_fields: Optional[List[str]] = None,
        region: str = None,
    ):
        """
        A common method to check which fields have the "yellow highlight". This is used in both CC and Address pages.

        Arguments:
            fields_to_test: The primary list of fields for this page (cc fields, address fields).
            expected_highlighted_fields: Which ones are expected to be highlighted. Defaults to all in `fields_to_test`.
            extra_fields: If some pages have extra fields to test (e.g. 'cc-csc'), pass them here.
            region: region to test
        """

        if not self.field_mapping:
            raise NotImplementedError(
                "Method should only be called in inherited classes."
            )

        if fields_to_test is None:
            fields_to_test = self.fields

        if region in ["DE", "FR"] and "address-level1" in fields_to_test:
            fields_to_test.remove("address-level1")

        if expected_highlighted_fields is None:
            # By default, everything in fields_to_test is expected to be highlighted
            expected_highlighted_fields = fields_to_test

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

    def verify_all_fields_cleared(self):
        """
        Verifies that all autofill fields are empty.
        """
        for field_name in self.field_mapping.keys():
            value = self.get_element("form-field", labels=[field_name]).get_attribute(
                "value"
            )
            assert not value, f"Field '{field_name}' is not empty: Found '{value}'"

    @BasePage.context_chrome
    def verify_autofill_data_on_hover(
        self, autofill_data: CreditCardBase | AutofillAddressBase
    ):
        """
        Abstract Method meant to be implemented in the inherited classes.
        Verifies autofill data when hovering over a field.
        """
        raise NotImplementedError("Method should be implemented in inherited classes.")

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

    def fill_and_save(
        self, region: str = "US", door_hanger: bool = True
    ) -> AutofillAddressBase | CreditCardBase:
        """
        Fills form with randomly generated data and interacts with the autofill popup.

        Arguments:
            region: Country code in use
            door_hanger: check to click save on door hanger
        """
        autofill_data = (
            self.util.fake_autofill_data(region)
            if self.__class__ == AddressFill
            else self.util.fake_credit_card_data(region)
        )
        self.fill_and_submit(autofill_data)
        if door_hanger:
            self.autofill_popup.click_doorhanger_button("save")
        return autofill_data

    def update_and_save(self, field: str, value: str | int, door_hanger: bool = True):
        """
        Update form with new field value and save.

        Arguments:
            field: field label.
            value: new value to be updated.
            door_hanger: bool to indication interaction with door_hanger.
        """
        self._fill_input_element(field, value)
        self._click_form_button("submit")

        if door_hanger:
            if field == "cc-number":
                self.autofill_popup.click_doorhanger_button("save")
            else:
                self.autofill_popup.click_doorhanger_button("update")

    def check_autofill_preview_for_field(
        self,
        field_label: str,
        sample_data: CreditCardBase | AutofillAddressBase,
        region: str = None,
    ):
        """
        Check that hovering over a field autofill option will prefill the other fields.

        Arguments:
            field_label: field name.
            sample_data: autofill sample data.
            region: region being tested.
        """
        if (
            self.__class__ == AddressFill
            and field_label == "address-level1"
            and region in ["DE", "FR"]
        ):
            return
        self.double_click("form-field", labels=[field_label])
        self.autofill_popup.ensure_autofill_dropdown_visible()
        self.autofill_popup.hover("select-form-option")
        self.verify_autofill_data_on_hover(sample_data)

    def clear_and_verify_all_fields(
        self,
        sample_data: AutofillAddressBase | CreditCardBase = None,
        region: str = None,
    ):
        """
        Autofill all form fields and verifies that they are empty.

        Arguments:
            region: region being tested
            sample_data: verify autofill against sample data if present
        """
        for field in self.fields:
            self.clear_and_verify(field, sample_data, region)

    def clear_and_verify(
        self,
        field_label: str,
        sample_data: CreditCardBase | AutofillAddressBase = None,
        region: str = None,
    ):
        """
        Autofills a form field, clears it, and verifies that it is empty.
        If sample data is present, will verify that data is filled correctly.

        Arguments:
            field_label : The label of the field being autofilled.
            region : region being tested
            sample_data: sample data for cc or address form.
        """
        # Skip address-level1 (State) selection for DE and FR
        if (
            region in ["DE", "FR"]
            and self.__class__ == AddressFill
            and field_label == "address-level1"
        ):
            return

        # Double-click a field and choose the first element from the autocomplete dropdown
        self.double_click("form-field", labels=[field_label])
        self.autofill_popup.ensure_autofill_dropdown_visible()
        self.autofill_popup.select_nth_element(1)

        if sample_data:
            ## verify data
            self.verify_form_data(sample_data)

        # Clear form autofill
        self.double_click("form-field", labels=[field_label])
        self.autofill_popup.ensure_autofill_dropdown_visible()
        self.autofill_popup.click_clear_form_option()

        # Verify all fields are cleared
        self.verify_all_fields_cleared()

    def generate_field_data(
        self, sample_data: AutofillAddressBase | CreditCardBase, field: str, region: str
    ) -> str | int:
        """
        Generates a new data for sample data according to field given, updates the information in the form.

        Arguments:
            sample_data: sample data instance being updated
            field: field being updated
            region: region being tested
        """
        faker_method = (
            self.util.fake_credit_card_data
            if self.__class__ == CreditCardFill
            else self.util.fake_autofill_data
        )
        new_sample_data_value = getattr(
            faker_method(country_code=region), self.field_mapping[field]
        )
        while new_sample_data_value == getattr(sample_data, self.field_mapping[field]):
            new_sample_data_value = getattr(
                faker_method(country_code=region), self.field_mapping[field]
            )

        setattr(sample_data, self.field_mapping[field], new_sample_data_value)
        return new_sample_data_value


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

    @BasePage.context_chrome
    def verify_autofill_data_on_hover(self, autofill_data: CreditCardBase):
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


class LoginAutofill(Autofill):
    """
    Page Object Model for the form autofill demo page with many logins
    """

    URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/password_manager/login_and_pw_change_forms.html"

    class LoginForm:
        """
        Subclass of the Login Autofill Form where you can interact with the Login Form
        """

        def __init__(self, parent: "LoginAutofill") -> None:
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
