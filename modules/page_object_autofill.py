import logging
from typing import List

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

    URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/"

    def fill_input_element(self, ba: BrowserActions, field_name: str, term: str):
        """
        Given BrowserActions object, the string of the element to be identified and the string term to be sent to the
        input, identify the webelement and send the term to the input field without any additional keystrokes.

        ...
        Attributes
        ----------
        ba : BrowserActions
        field_name : str
            The name of the input field to be identified
        term: str
            The string to be sent to the input field
        """
        form_field_element = self.get_element("form-field", labels=[field_name])
        ba.clear_and_fill(form_field_element, term, press_enter=False)

    def click_form_button(self, field_name):
        """Clicks submit on the form"""
        self.click_on("submit-button", labels=[field_name])


class CreditCardFill(Autofill):
    """
    Page Object Model for auto site (https://mozilla.github.io/form-fill-examples/basic_cc.html)
    """

    URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/basic_cc.html"
    fields = ["cc-name", "cc-number", "cc-exp-month", "cc-exp-year"]

    def fill_credit_card_info(self, info: CreditCardBase):
        """
        Fills a credit card form with the provided information.

        ...

        Attributes
        ----------
        info:  CreditCardBase
            An instance of the CreditCardBase class containing the credit card details.

        """
        fields = {
            "cc-name": info.name,
            "cc-number": info.card_number,
            "cc-exp-month": info.expiration_month,
            "cc-exp-year": info.expiration_year,
            "cc-csc": info.cvv,
        }
        ba = BrowserActions(self.driver)
        for field, value in fields.items():
            if value is not None:
                self.fill_input_element(ba, field, value)

        self.click_form_button("submit")

    def verify_autofill_dropdown_all_fields(self, ccp: AutofillPopup):
        """Given a CreditCardPopup object, verify all fields"""
        for field in self.fields:
            self.double_click("form-field", labels=[field])
            ccp.ensure_autofill_dropdown_visible()
        # Ensure 'cc-csc' does NOT trigger the autofill dropdown
        self.double_click("form-field", labels=["cc-csc"])
        ccp.ensure_autofill_dropdown_not_visible()

    def verify_four_fields(
        self, ccp: AutofillPopup, credit_card_sample_data: CreditCardBase
    ) -> Autofill:
        """
        Verifies that after clicking the autofill panel the information is filled correctly.

        Attributes
        ----------

        ccp: CreditCardPopup
            The credit card popup object

        credit_card_sample_data: CreditCardBase
            The object that contains all the relevant information about the credit card autofill
        """
        self.double_click("form-field", labels=["cc-name"])
        info_list = self.extract_credit_card_obj_into_list(credit_card_sample_data)
        # Click on popup form value with name only
        if self.sys_platform() == "Linux":
            with self.driver.context(self.driver.CONTEXT_CHROME):
                ccp.custom_wait(timeout=30, poll_frequency=0.5).until(
                    EC.element_to_be_clickable(
                        ccp.get_selector(
                            "select-form-option-by-value", labels=[info_list[0]]
                        )
                    )
                )
        ccp.click_on("select-form-option-by-value", labels=[info_list[0]])

        for i in range(len(info_list)):
            self.element_attribute_contains(
                "form-field", "value", info_list[i], labels=[self.fields[i]]
            )
        return self

    def fake_and_fill(
        self, util: Utilities, autofill_popup_obj: AutofillPopup
    ) -> CreditCardBase:
        """
        Fills a credit card form with randomly generated data and interacts with the autofill popup.

        ...

        Parameters
        ----------

        util: Utilities
            An instance of the Utilities class
        autofill_popup_obj: AutofillPopup
            An instance of the AutofillPopup class used to interact with the autofill popup
        """
        credit_card_sample_data = util.fake_credit_card_data()
        self.fill_credit_card_info(credit_card_sample_data)
        autofill_popup_obj.click_doorhanger_button("save")
        return credit_card_sample_data

    def update_field(
        self, field: str, field_data: str, autofill_popup_obj: AutofillPopup
    ):
        """
        Updates a field in the form with given data.

        ...

        Parameters
        ----------

        field: str
            The name of the field to fill

        field_data: str
            The data to put in the field

        autofill_popup_obj: AutofillPopup
            Instantiated AutofillPopup object that describes the existing popup
        """
        ba = BrowserActions(self.driver)
        self.fill_input_element(ba, field, field_data)
        self.click_form_button("submit")

    def press_autofill_panel(self, credit_card_popoup_obj: AutofillPopup):
        """
        Presses the autofill panel that pops up after you double-click an input field
        """
        self.double_click("form-field", labels=["cc-name"])
        with self.driver.context(self.driver.CONTEXT_CHROME):
            credit_card_popoup_obj.get_element("select-form-option").click()

    def update_credit_card_information(
        self,
        autofill_popup_obj: AutofillPopup,
        field_name: str,
        field_data: str,
        save_card=False,
    ):
        """
        Updates the credit card based on field that is to be changed by first autofilling everything then updating
        the field of choice then pressing submit and handling the popup.
        """
        self.press_autofill_panel(autofill_popup_obj)
        self.update_field(field_name, field_data, autofill_popup_obj)
        self.click_form_button("submit")

        if not save_card:
            autofill_popup_obj.click_on("update-card-info-popup-button")
        else:
            autofill_popup_obj.click_on("doorhanger-save-button")

    def extract_credit_card_obj_into_list(
        self, credit_card_sample_data: CreditCardBase
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
        self,
        autofill_popup_obj: AutofillPopup,
        credit_card_sample_data: CreditCardBase,
        field_name: str,
        new_data: str,
    ) -> Autofill:
        """
        Verifies that there is only 1 profile in the popup panel, updates the credit card information and verifies all
        the fields according to the passed in credit card information object

        Attributes
        ----------

        autofill_popup_obj: AutofillPopup
            An instance of autofill popup object

        credit_card_sample_data: CreditCardBase
            An instance of the fake generated data

        field_name: str
            The name of the field to update

        new_data: str
            The data to update the field with
        """

        # updating the profile accordingly
        self.update_credit_card_information(autofill_popup_obj, field_name, new_data)

        # verifying the correct data
        self.verify_four_fields(autofill_popup_obj, credit_card_sample_data)
        return self

    def update_cc_name(
        self,
        util: Utilities,
        credit_card_sample_data: CreditCardBase,
        autofill_popup_obj: AutofillPopup,
    ) -> Autofill:
        """
        Generates a new name, updates the credit card information in the form.
        """
        new_cc_name = util.fake_credit_card_data().name
        credit_card_sample_data.name = new_cc_name

        self.verify_updated_information(
            autofill_popup_obj,
            credit_card_sample_data,
            "cc-name",
            credit_card_sample_data.name,
        )
        return self

    def update_cc_exp_month(
        self,
        util: Utilities,
        credit_card_sample_data: CreditCardBase,
        autofill_popup_obj: AutofillPopup,
    ) -> Autofill:
        """
        Generates a new expiry month, updates the credit card information in the form.
        """
        new_cc_exp_month = util.fake_credit_card_data().expiration_month
        credit_card_sample_data.expiration_month = new_cc_exp_month

        self.verify_updated_information(
            autofill_popup_obj,
            credit_card_sample_data,
            "cc-exp-month",
            credit_card_sample_data.expiration_month,
        )
        return self

    def update_cc_exp_year(
        self,
        util: Utilities,
        credit_card_sample_data: CreditCardBase,
        autofill_popup_obj: AutofillPopup,
    ) -> Autofill:
        """
        Generates a new expiry year, updates the credit card information in the form.
        """
        new_cc_exp_year = util.fake_credit_card_data().expiration_year
        credit_card_sample_data.expiration_year = new_cc_exp_year

        self.verify_updated_information(
            autofill_popup_obj,
            credit_card_sample_data,
            "cc-exp-year",
            credit_card_sample_data.expiration_year,
        )
        return self

    def verify_clear_form_all_fields(self, autofill_popup_obj: AutofillPopup):
        """
        Clears all fields in the form by triggering the clear action from each field in turn. After each clear
        action, verifies that all fields are empty, regardless of which field initiated the clear.
        """
        for field in self.fields:
            self.click_on("form-field", labels=[field])
            autofill_popup_obj.click_autofill_form_option()
            self.click_on("form-field", labels=[field])
            autofill_popup_obj.click_clear_form_option()
            # Verify that all fields are blank
            for f in self.fields:
                self.element_attribute_contains("form-field", "value", "", labels=[f])
            # Verify that the 'cc-csc' field does not trigger an autofill dropdown
            self.double_click("form-field", labels=["cc-csc"])
            autofill_popup_obj.ensure_autofill_dropdown_not_visible()

    def verify_field_yellow_highlights(self, expected_highlighted_fields=None):
        """
        Verifies that specified form fields have the expected highlight state
        """
        if expected_highlighted_fields is None:
            expected_highlighted_fields = self.fields

        browser_action_obj = BrowserActions(self.driver)

        # Check if a color is yellow-ish
        def is_yellow_highlight(rgb_tuple):
            if len(rgb_tuple) == 3:
                r, g, b = rgb_tuple
            elif len(rgb_tuple) >= 4:
                r, g, b, *_ = rgb_tuple
            else:
                return False
            # Uses a tolerance to detect a yellow highlight
            return r >= 250 and g >= 250 and 180 < b < 220

        all_fields = self.fields + ["cc-csc"]

        for field_name in all_fields:
            # Bring the fields into focus
            self.click_on("form-field", labels=[field_name])

            # Get the color of the fields
            selector = self.get_selector("form-field", labels=[field_name])
            colors = browser_action_obj.get_all_colors_in_element(selector)
            logging.info(f"Colors found in {field_name}: {colors}")

            is_field_highlighted = any(is_yellow_highlight(color) for color in colors)
            should_be_highlighted = field_name in expected_highlighted_fields

            if should_be_highlighted:
                assert is_field_highlighted, (
                    f"Expected yellow highlight on {field_name}, but none found."
                )
                logging.info(f"Yellow highlight correctly found in {field_name}.")
            else:
                assert not is_field_highlighted, (
                    f"Expected no yellow highlight on {field_name}, but found one."
                )
                logging.info(f"No yellow highlight found in {field_name}, as expected.")

        return self


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


class AddressFill(Autofill):
    """
    Page Object Model for auto site (https://mozilla.github.io/form-fill-examples/basic.html)
    """

    URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/basic.html"

    def save_information_basic(self, autofill_info: AutofillAddressBase):
        """
        Saves information passed in, in the form of an AutofillAddressBase object.
        Instantiates a dictionary of fields and fills in the input, if the input is not None.

        ...
        Attributes
        ---------

        autofill_info: AutofillAddressBase
        """
        ba = BrowserActions(self.driver)
        fields = {
            "name": autofill_info.name,
            "organization": autofill_info.organization,
            "street-address": autofill_info.street_address,
            "address-level2": autofill_info.address_level_2,
            "address-level1": autofill_info.address_level_1,
            "postal-code": autofill_info.postal_code,
            "country": autofill_info.country,
            "email": autofill_info.email,
            "tel": autofill_info.telephone,
        }

        for field, value in fields.items():
            if value is not None:
                self.fill_input_element(ba, field, value)

        self.click_form_button("submit")

    def verify_autofill_displayed(self):
        """
        Verifies that the autofill suggestions are displayed.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            element = self.get_element("select-address")
            self.expect(EC.visibility_of(element))

    def send_keys_to_element(self, name: str, label: str, keys: str):
        """
        Send keys to the specified element.
        """
        elem = self.get_element(name, labels=[label])
        current_value = elem.get_attribute("value")
        new_value = current_value + keys
        elem.clear()
        elem.send_keys(new_value)

    def verify_autofill_data(
        self, autofill_data: AutofillAddressBase, region: str, util: Utilities
    ):
        """
        Verifies that the autofill data matches the expected values.

        :param autofill_data: AutofillAddressBase object containing expected data.
        :param region: The region code (e.g., "US", "DE", "FR").
        :param util: Utilities instance to normalize values.
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
            "Country": autofill_data.country,
            "Email": autofill_data.email,
            "Phone": util.normalize_phone_number(autofill_data.telephone),
        }

        # Validate each field
        for field, expected in expected_values.items():
            actual = actual_values[field]

            # Skip State verification for DE and FR
            if field == "State" and region in ["DE", "FR"]:
                continue

            # Normalize phone numbers before comparison
            if field == "Phone":
                actual = util.normalize_phone_number(actual)

            assert actual == expected, (
                f"Mismatch in {field}: Expected '{expected}', but got '{actual}'"
            )


class TextAreaFormAutofill(Autofill):
    """
    Page Object Model for the form autofill demo page with a textarea
    """

    URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/textarea_select.html"
