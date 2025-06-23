import json
import logging
from typing import List, Optional

from selenium.webdriver import Firefox
from selenium.webdriver.support.select import Select

from modules.browser_object_autofill_popup import AutofillPopup
from modules.classes.autofill_base import AutofillAddressBase
from modules.classes.credit_card import CreditCardBase
from modules.page_base import BasePage
from modules.util import BrowserActions, Utilities

BASE_CC_URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/basic_cc.html"
BASE_ADDRESS_URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/basic.html"

# Class Attributes: Element Selectors
base_cc_field_mapping = {
    "name": "cc-name",
    "card_number": "cc-number",
    "expiration_month": "cc-exp-month",
    "expiration_year": "cc-exp-year",
    "cvv": "cc-csc",
}
base_address_field_mapping = {
    "name": "name",
    "organization": "organization",
    "street_address": "street-address",
    "address_level_2": "address-level2",
    "address_level_1": "address-level1",
    "postal_code": "postal-code",
    "country_code": "country",
    "email": "email",
    "telephone": "tel",
}

# Element Selectors
base_cc_fields = ["cc-name", "cc-number", "cc-exp-month", "cc-exp-year"]
base_address_fields = [
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

# Preview field mappings
base_preview_address_mapping = {
    "family_name": "family-name",
    "given_name": "given-name",
    "street_address": "street-address",
    "address_level_2": "address-level2",
    "address_level_1": "address-level1",
    "postal_code": "postal-code",
    "country_code": "country",
    "telephone": "tel",
}
base_preview_cc_mapping = {
    "name": "cc-name",
    "card_number": "cc-number",
    "expiration_month": "cc-exp-month",
    "expiration_year": "cc-exp-year",
}


class Autofill(BasePage):
    """
    Page Object Model for auto site (https://mozilla.github.io/form-fill-examples/) base parent object of all
    autofill page related objects
    """

    # Default; subclasses will override
    field_mapping = {}
    fields = {}
    preview_fields = {}

    URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/"

    def __init__(self, driver: Firefox, **kwargs):
        super().__init__(driver, **kwargs)
        self.driver = driver
        self.browser_actions = BrowserActions(self.driver)
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
        if form_field_element.tag_name.lower() == "select":
            selected_form = Select(form_field_element)
            shortened_state = self.util.get_state_province_abbreviation(term)
            selected_form.select_by_value(shortened_state)
        else:
            self.browser_actions.clear_and_fill(
                form_field_element, term, press_enter=False
            )

    def scroll_to_form_field(self):
        """
        Scrolls to the first available field value.
        Note: First field in mapping must be the first field that is visible to be selected.
        """
        if not self.field_mapping:
            # Method is meant to be called by one of the classes that inherit AutoFill (CreditCardFill or AddressFill)
            # Should not be called directly from an Autofill instance.
            raise NotImplementedError(
                "Method should only be called in inherited classes."
            )
        first_field = self.get_element("form-field", labels=[self.fields[0]])
        self.driver.execute_script("arguments[0].scrollIntoView();", first_field)
        return self

    def _click_form_button(self, field_name):
        """Clicks submit on the form"""
        self.element_clickable("submit-button", labels=[field_name])
        self.click_on("submit-button", labels=[field_name])

    def is_field_present(self, attr_name: str):
        """checks whether the attribute name exists in the mapping."""
        field = self.field_mapping.get(attr_name, None)
        return True if field else False

    def select_first_form_field(self, autofill: bool = False):
        """
        Click first available form field option.
        If autofill flag is true, select autofill option for first available field.
        """
        if autofill:
            self.select_autofill_option(self.fields[0])
        else:
            self.click_form_field(self.fields[0])
        return self

    def click_form_field(self, attr_name: str):
        """Click the form field given the attribute name."""
        field = self.field_mapping.get(attr_name, None)
        if field:
            self.double_click("form-field", labels=[field])
        else:
            logging.warning(f"The field: {attr_name} is not available in the site.")

    def verify_no_dropdown_on_field_interaction(self, attr_name):
        """
        Click on the form field given the attribute name and ensure that the field
        does not activate the dropdown.
        """
        field = self.field_mapping.get(attr_name, None)
        if field:
            self.double_click("form-field", labels=[field])
            self.autofill_popup.ensure_autofill_dropdown_not_visible()
        else:
            logging.warning(f"The field: {attr_name} is not available in the site.")

    def fill_and_submit(self, data_object: CreditCardBase | AutofillAddressBase | dict):
        """Fill and submit from data object or dictionary.

        Arguments:
            data_object: object containing autofill data.
        """
        if not self.field_mapping:
            # Method is meant to be called by one of the classes that inherit AutoFill (CreditCardFill or AddressFill)
            # Should not be called directly from an Autofill instance.
            raise NotImplementedError(
                "Method should only be called in inherited classes."
            )
        for attr_name, field_name in self.field_mapping.items():
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
            # Method is meant to be called by one of the classes that inherit AutoFill (CreditCardFill or AddressFill)
            # Should not be called directly from an Autofill instance.
            raise NotImplementedError(
                "Method should only be called in inherited classes."
            )

        is_address_fill = self.__class__ == AddressFill
        non_us_ca_address = is_address_fill and sample_data.country_code not in [
            "US",
            "CA",
        ]
        for attr_name, field_name in self.field_mapping.items():
            if non_us_ca_address and field_name == "address-level1":
                continue
            if attr_name == "cvv":
                continue
            expected_value = getattr(sample_data, attr_name, None)
            autofilled_field = self.get_element("form-field", labels=[field_name])
            if autofilled_field.tag_name.lower() != "select":
                autofilled_field_value = autofilled_field.get_attribute("value")
            else:
                autofilled_field_value = Select(
                    autofilled_field
                ).first_selected_option.text
            if (
                field_name == "address-level1"
                and autofilled_field_value != expected_value
            ):
                expected_value = self.util.get_state_province_abbreviation(
                    expected_value
                )
            assert expected_value in autofilled_field_value, (
                f"{autofilled_field_value} is different from {expected_value}"
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
            # Method is meant to be called by one of the classes that inherit AutoFill (CreditCardFill or AddressFill)
            # Should not be called directly from an Autofill instance.
            raise NotImplementedError(
                "Method should only be called in inherited classes."
            )

        if fields_to_test is None:
            fields_to_test = [x for x in self.field_mapping.keys() if x != "cvv"]

        # Handle region-specific behavior
        if region not in {"US", "CA"} and "address_level_1" in fields_to_test:
            fields_to_test.remove("address_level_1")

        # Check fields that SHOULD trigger the autofill dropdown
        for field_name in fields_to_test:
            field = self.field_mapping.get(field_name, None)
            # How do i simplify this logic?
            if field:
                autofill_field = self.get_element("form-field", labels=[field])
                if autofill_field.tag_name.lower() != "select":
                    # more general way of activating the dropdown
                    self.double_click("form-field", labels=[field])
                    autofill_field.send_keys("")
                    self.autofill_popup.ensure_autofill_dropdown_visible()
                    logging.info(f"Autofill dropdown appears for field '{field}'.")
                else:
                    logging.info(
                        f"Field: {field_name} is a select element. No autofill option."
                    )
            else:
                logging.warning(
                    f"The field: {field_name} is not available in the site."
                )

        # Check fields that should NOT trigger the autofill dropdown
        if excluded_fields:
            for field_name in excluded_fields:
                field = self.field_mapping.get(field_name, None)
                if field:
                    self.double_click("form-field", labels=[field_name])
                    self.autofill_popup.ensure_autofill_dropdown_not_visible()
                    logging.info(
                        f"No autofill dropdown appears for field '{field_name}', as expected."
                    )
                else:
                    logging.warning(
                        f"The field: {field_name} is not available in the site."
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
            # Method is meant to be called by one of the classes that inherit AutoFill (CreditCardFill or AddressFill)
            # Should not be called directly from an Autofill instance.
            raise NotImplementedError(
                "Method should only be called in inherited classes."
            )

        if fields_to_test is None:
            fields_to_test = set(self.field_mapping.keys())

        if region not in {"US", "CA"} and "address_level_1" in fields_to_test:
            fields_to_test.remove("address_level_1")

        if expected_highlighted_fields is None:
            # By default, everything in fields_to_test is expected to be highlighted except cvv for cc
            expected_highlighted_fields = fields_to_test
            if "cvv" in expected_highlighted_fields:
                expected_highlighted_fields.remove("cvv")

        if extra_fields:
            fields_to_actually_check = fields_to_test + extra_fields
        else:
            fields_to_actually_check = fields_to_test

        def is_yellow_highlight(rgb_tuple):
            """
            Returns True if the color tuple is bright yellow-ish.
            """
            if len(rgb_tuple) == 3:
                r, g, b = rgb_tuple
            else:
                r, g, b, *_ = rgb_tuple

            return (r >= 250) and (g >= 250) and (180 < b < 220)

        for field_name in fields_to_actually_check:
            field = self.field_mapping.get(field_name, None)
            if field:
                autofill_field = self.get_element("form-field", labels=[field])
                if autofill_field.tag_name.lower() != "select":
                    # Focus the field so the highlight is visible
                    self.click_on("form-field", labels=[field])

                    # Get all colors in the field
                    selector = self.get_selector("form-field", labels=[field])
                    colors = self.browser_actions.get_all_colors_in_element(selector)
                    logging.info(f"Colors found in '{field}': {colors}")

                    # Check the highlight
                    is_field_highlighted = any(
                        is_yellow_highlight(color) for color in colors
                    )
                    should_be_highlighted = field_name in expected_highlighted_fields

                    # Assert based on expectation
                    if should_be_highlighted:
                        assert is_field_highlighted, (
                            f"Expected yellow highlight on '{field}', but none found."
                        )
                        logging.info(f"Yellow highlight found in '{field}'.")
                    else:
                        assert not is_field_highlighted, (
                            f"Expected NO yellow highlight on '{field}', but found one."
                        )
                        logging.info(f"No yellow highlight in '{field}', as expected.")
                else:
                    logging.info(
                        f"Field: {field} is a select element. No autofill option."
                    )
            else:
                logging.warning(f"The field: {field} is not available in the site.")

        return self

    def verify_all_fields_cleared(self):
        """
        Verifies that all autofill fields are empty.
        """
        for field_name in self.fields:
            field_element = self.get_element("form-field", labels=[field_name])
            value = field_element.get_attribute("value")
            if field_element.tag_name.lower() != "select":
                assert not value, f"Field '{field_name}' is not empty: Found '{value}'"

    @BasePage.context_chrome
    def verify_autofill_data_on_hover(
        self, autofill_data: CreditCardBase | AutofillAddressBase
    ):
        """
        Verifies that the autofill preview data matches the expected values when hovering

        Arguments:
            autofill_data: CreditCardBase | AutofillAddressBase object containing expected fake data.
        """
        # Get preview data from hovering through the chrome context
        try:
            # Attempt to parse the string as JSON
            container = json.loads(
                self.autofill_popup.get_element("preview-form-container").get_attribute(
                    "ac-comment"
                )
            )
        except json.JSONDecodeError:
            # If parsing fails, raise ValueError.
            raise ValueError("Given preview data is incomplete.")
        container_data = container.get("fillMessageData", {}).get("profile", {})
        assert container_data, "No preview data available."
        assert all(field in container_data.keys() for field in self.preview_fields), (
            "Not all fields present in preview data."
        )

        # sanitize data
        if autofill_data.__class__ == CreditCardBase:
            autofill_data.card_number = autofill_data.card_number[-4:]
        else:
            if autofill_data.country_code in {"US", "CA"} and (
                len(container_data["address-level1"]) == 2
                and len(autofill_data.address_level_1) > 2
            ):
                autofill_data.address_level_1 = (
                    self.util.get_state_province_abbreviation(
                        autofill_data.address_level_1
                    )
                )
        for field, value in container_data.items():
            if field in self.preview_fields:
                value = self.sanitize_preview_data(field, str(value))
                # Check if this value exists in our CreditCardBase | AutofillAddressBase object
                is_present = any(
                    [value in val for val in autofill_data.__dict__.values()]
                )
                assert is_present, (
                    f"Mismatched data: {(field, value)} not in {autofill_data.__dict__.values()}."
                )

    def sanitize_preview_data(self, field, value):
        if field == "cc-number":
            value = value[-4:]
        elif field == "cc-exp-year":
            value = value[-2:]
        elif value[0] == "+":
            value = self.util.normalize_phone_number(value)
        return value

    def select_autofill_option(self, field, index: int = 1):
        """
        Presses the autofill panel that pops up after you double-click an input field

        Argument:
            autofill_popup: AutofillPopup
            field:  field to click to show autofill option.
            index: which autofill option to pick.
        """
        autofill_field = self.get_element("form-field", labels=[field])
        if autofill_field.tag_name.lower() != "select":
            self.double_click("form-field", labels=[field])
            self.autofill_popup.ensure_autofill_dropdown_visible()
            self.autofill_popup.select_nth_element(index)
        else:
            logging.info(f"Field: {field} is a select element. No autofill option.")
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
            and field_label == "address_level_1"
            and region not in {"US", "CA"}
        ):
            return
        field = self.field_mapping.get(field_label, None)
        if field:
            autofill_field = self.get_element("form-field", labels=[field])
            if autofill_field.tag_name.lower() != "select":
                self.double_click("form-field", labels=[field])
                self.autofill_popup.ensure_autofill_dropdown_visible()
                self.autofill_popup.hover("select-form-option")
                self.verify_autofill_data_on_hover(sample_data)
                self.click_on("form-field", labels=[field])
            else:
                logging.info(
                    f"Field: {field_label} is a select element. No autofill option."
                )
        else:
            logging.info(f"The field: {field_label} is not present in the site.")

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
        fields = [x for x in self.field_mapping.keys() if x != "cvv"]
        for field in fields:
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
            region not in {"US", "CA"}
            and self.__class__ == AddressFill
            and field_label == "address_level_1"
        ):
            return

        field = self.field_mapping.get(field_label, None)
        if field:
            autofill_field = self.get_element("form-field", labels=[field])
            if autofill_field.tag_name.lower() != "select":
                # Double-click a field and choose the first element from the autocomplete dropdown
                self.double_click("form-field", labels=[field])
                self.autofill_popup.ensure_autofill_dropdown_visible()
                self.autofill_popup.select_nth_element(1)

                if sample_data:
                    ## verify data
                    self.verify_form_data(sample_data)

                # Clear form autofill
                self.double_click("form-field", labels=[field])
                self.autofill_popup.ensure_autofill_dropdown_visible()
                self.autofill_popup.click_clear_form_option()

                # Verify all fields are cleared
                self.verify_all_fields_cleared()
            else:
                logging.info(
                    f"Field: {field_label} is a select element. No autofill option."
                )
        else:
            logging.warning(f"The field: {field_label} is not available in the site.")

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
        inverted_mapping = {v: k for k, v in self.field_mapping.items()}
        new_sample_data_value = getattr(
            faker_method(country_code=region), inverted_mapping[field]
        )
        while new_sample_data_value == getattr(sample_data, inverted_mapping[field]):
            new_sample_data_value = getattr(
                faker_method(country_code=region), inverted_mapping[field]
            )

        setattr(sample_data, inverted_mapping[field], new_sample_data_value)
        return new_sample_data_value


class AddressFill(Autofill):
    """
    Page Object Model for address autofill site.
    base site is: (https://mozilla.github.io/form-fill-examples/basic.html)
    """

    def __init__(
        self,
        driver: Firefox,
        url_template=None,
        field_mapping=None,
        fields=None,
        **kwargs,
    ):
        super().__init__(driver, **kwargs)
        self.field_mapping = (
            field_mapping if field_mapping else base_address_field_mapping
        )
        self.fields = fields if fields else base_address_fields
        self.preview_fields = set(
            map(
                lambda field: base_preview_address_mapping.get(field, field),
                self.field_mapping.keys(),
            )
        )
        self.URL_TEMPLATE = url_template if url_template else BASE_ADDRESS_URL_TEMPLATE


class CreditCardFill(Autofill):
    """
    Page Object Model for cc autofill site
    base site is: (https://mozilla.github.io/form-fill-examples/basic_cc.html)
    """

    def __init__(
        self,
        driver: Firefox,
        url_template=None,
        field_mapping=None,
        fields=None,
        **kwargs,
    ):
        super().__init__(driver, **kwargs)
        self.field_mapping = field_mapping if field_mapping else base_cc_field_mapping
        self.fields = fields if fields else base_cc_fields
        self.preview_fields = set(
            map(
                lambda field: base_preview_cc_mapping.get(field),
                self.field_mapping.keys(),
            )
        )
        self.preview_fields = {
            field for field in self.preview_fields if field is not None
        }
        self.URL_TEMPLATE = url_template if url_template else BASE_CC_URL_TEMPLATE


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
