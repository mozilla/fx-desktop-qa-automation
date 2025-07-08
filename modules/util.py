import base64
import json
import logging
import os
import platform
import re
from os import remove
from random import shuffle
from time import sleep
from typing import List, Literal, Union
from urllib.parse import urlparse, urlunparse

from faker import Faker
from faker.config import AVAILABLE_LOCALES
from faker.providers import internet, misc
from jsonpath_ng import parse
from PIL import Image
from selenium.common.exceptions import (
    InvalidArgumentException,
    WebDriverException,
)
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.shadowroot import ShadowRoot
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from modules.classes.autofill_base import AutofillAddressBase
from modules.classes.credit_card import CreditCardBase


class Utilities:
    """
    Methods that may be useful, that have nothing to do with Selenium.
    """

    def __init__(self):
        self.state_province_abbr = {
            # US States
            "Alabama": "AL",
            "Alaska": "AK",
            "Arizona": "AZ",
            "Arkansas": "AR",
            "California": "CA",
            "Colorado": "CO",
            "Connecticut": "CT",
            "Delaware": "DE",
            "Florida": "FL",
            "Georgia": "GA",
            "Hawaii": "HI",
            "Idaho": "ID",
            "Illinois": "IL",
            "Indiana": "IN",
            "Iowa": "IA",
            "Kansas": "KS",
            "Kentucky": "KY",
            "Louisiana": "LA",
            "Maine": "ME",
            "Maryland": "MD",
            "Massachusetts": "MA",
            "Michigan": "MI",
            "Minnesota": "MN",
            "Mississippi": "MS",
            "Missouri": "MO",
            "Montana": "MT",
            "Nebraska": "NE",
            "Nevada": "NV",
            "New Hampshire": "NH",
            "New Jersey": "NJ",
            "New Mexico": "NM",
            "New York": "NY",
            "North Carolina": "NC",
            "North Dakota": "ND",
            "Ohio": "OH",
            "Oklahoma": "OK",
            "Oregon": "OR",
            "Pennsylvania": "PA",
            "Rhode Island": "RI",
            "South Carolina": "SC",
            "South Dakota": "SD",
            "Tennessee": "TN",
            "Texas": "TX",
            "Utah": "UT",
            "Vermont": "VT",
            "Virginia": "VA",
            "Washington": "WA",
            "West Virginia": "WV",
            "Wisconsin": "WI",
            "Wyoming": "WY",
            # Canadian Provinces
            "Alberta": "AB",
            "British Columbia": "BC",
            "Manitoba": "MB",
            "New Brunswick": "NB",
            "Newfoundland and Labrador": "NL",
            "Nova Scotia": "NS",
            "Ontario": "ON",
            "Prince Edward Island": "PE",
            "Quebec": "QC",
            "Saskatchewan": "SK",
            "Northwest Territories": "NT",
            "Nunavut": "NU",
            "Yukon": "YT",
        }
        # temporary fix until faker issue is resolved
        self.country_local_translation = {"Germany": "Deutschland"}
        self.fake = None
        self.locale = None

    def assert_search_code_in_url(self, driver, nav, expected_code):
        assert expected_code in driver.current_url, (
            f"Expected '{expected_code}' in URL, got: {driver.current_url}"
        )
        nav.clear_awesome_bar()

    def remove_file(self, path: str):
        try:
            os.remove(path)
            logging.info(path + " has been deleted.")
        except OSError as error:
            logging.warning("There was an error.")
            logging.warning(error)

    def get_saved_file_path(self, file_name: str) -> str:
        """
        Gets the saved location of a downloaded file depending on the OS.
        """
        saved_image_location = ""
        this_platform = platform.system()
        if this_platform == "Windows":
            user = os.environ.get("USERNAME")
            saved_image_location = f"C:\\Users\\{user}\\Downloads\\{file_name}"
        elif this_platform == "Darwin":
            user = os.environ.get("USER")
            saved_image_location = f"/Users/{user}/Downloads/{file_name}"
        elif this_platform == "Linux":
            user = os.environ.get("USER")
            saved_image_location = f"/home/{user}/Downloads/{file_name}"
        return saved_image_location

    def random_string(self, n: int) -> str:
        """A random string of n alphanum characters, including possible hyphen."""
        chars = list("bdehjlmptvwxz2678-BDEHJLMPTVWXZ")
        shuffle(chars)
        return "".join(chars[:n])

    def generate_random_text(
        self, type: Literal["word", "sentence", "paragraph"] = "word"
    ) -> str:
        """
        Generates a random word, sentence or paragraph based on what is passed in.
        """
        fake = Faker()
        if type == "word":
            return fake.word()
        elif type == "sentence":
            return fake.sentence()
        else:
            return fake.paragraph()

    def write_html_content(self, file_name: str, driver: Firefox, chrome: bool):
        """
        Takes the driver, the desired file name and the flag chrome, when true this flag will log the
        web contents of the Chrome in the <file_name>.html and the regular page contents when it is fales.

        ...

        Attributes
        ---------

        file_name : str
            The name of the file to be made
        driver : selenium.webdriver.Firefox
            The Firefox driver instance
        chrome : bool
            A boolean flag indicating whether or not to write contents of the browsers chrome
            when True, or the browser's content when False.
        """
        if chrome:
            with driver.context(driver.CONTEXT_CHROME):
                self.__write_contents(driver, file_name)
        else:
            self.__write_contents(driver, file_name)

    def __write_contents(self, driver: Firefox, file_name: str):
        """
        A private helper function to help write contents of a file from write_html_content

        ...

        Attributes
        ---------

        driver: selenium.webdriver.Firefox
            The Firefox driver instance
        file_name: str
            The name of the file to be made
        """
        with open(file_name + ".html", "w") as fh:
            output_contents = driver.page_source.replace("><", ">\n<")
            fh.write(output_contents)

    def create_localized_faker(self, country_code: str):
        """
        Given a country code, creates a Faker instance with the appropriate locale.
        Ensures valid Faker locale names are used.

        Returns:
        -------
        Optional[Tuple[Faker, bool]] -> (faker_instance, is_valid_locale) or None if invalid.
        """

        # Check if locale exists, otherwise return None
        locale = next(filter(lambda x: country_code in x, AVAILABLE_LOCALES), None)

        if not locale:
            logging.error(
                f"Invalid country code `{country_code}`. No faker instance created."
            )
            return None  # No fallback

        try:
            # seed to get consistent data
            if self.fake is None:
                if locale != self.locale:
                    Faker.seed(locale)
                    self.locale = locale
                self.fake = Faker(locale)
            faker = self.fake
            self.fake = faker
            faker.add_provider(internet)
            faker.add_provider(misc)
            return faker, True
        except AttributeError:
            logging.error(
                f"Invalid locale `{locale}`. Faker instance could not be created."
            )

            return None

    def generate_localized_phone(self, country_code: str, fake: Faker) -> str:
        """
        Generates a phone number that is valid based on country code

        For US and CA, this means that only numbers that do not start with 1 (in the actual phone number not the area code) are considered valid.

        ...
        Attributes
        ----------
        country_code: str
            The country code
        fake : Faker
            The localized Faker object

        Returns
        -------
        str
            The raw, generated phone number
        """
        if country_code in ["US", "CA"]:
            while True:
                phone = self.normalize_phone_number(fake.phone_number())
                if phone[:2] != "11":
                    break
        else:
            phone = self.normalize_regional_phone_numbers(
                fake.phone_number(), country_code
            )
        return phone

    def fake_autofill_data(self, country_code) -> AutofillAddressBase:
        """
        Generates fake autofill data for a given country code.
        """
        # valid attributes to get region for locale
        region_attributes = ["state", "administrative_unit", "region"]
        fake, valid_code = self.create_localized_faker(country_code)
        name = fake.name()
        given_name, family_name = name.split()
        organization = fake.company().replace(",", "")
        street_address = fake.street_address()
        # find correct attribute for selected locale
        valid_attribute = next(
            filter(lambda attr: hasattr(fake, attr), region_attributes), None
        )
        # set correct region if valid attribute is found else none
        address_level_1 = (
            getattr(fake, valid_attribute)() if valid_attribute else valid_attribute
        )
        address_level_2 = fake.city()
        postal_code = fake.postcode()
        country = fake.current_country()
        email = fake.email()
        telephone = self.generate_localized_phone(country_code, fake)

        fake_data = AutofillAddressBase(
            name=name,
            family_name=family_name,
            given_name=given_name,
            organization=organization,
            street_address=street_address,
            address_level_2=address_level_2,
            address_level_1=address_level_1,
            postal_code=postal_code,
            country=country,
            country_code=country_code,
            email=email,
            telephone=telephone,
        )

        return fake_data

    def fake_credit_card_data(
        self, country_code: str = "US", original_data: CreditCardBase = None
    ) -> CreditCardBase:
        """
        Generates fake information related to the CC scenarios for a given country code.


        Returns
        -------
        CreditCardBase
            The object that contains all the fake data generated.
        """
        fake, valid_code = self.create_localized_faker(country_code)
        name = fake.name()
        given_name, family_name = name.split()
        card_number = fake.credit_card_number()
        generated_credit_expiry = fake.credit_card_expire()
        expiration_month, expiration_year = generated_credit_expiry.split("/")
        cvv = fake.credit_card_security_code()
        telephone = self.generate_localized_phone(country_code, fake)

        fake_data = CreditCardBase(
            name=name,
            given_name=given_name,
            family_name=family_name,
            card_number=card_number,
            expiration_month=expiration_month,
            expiration_year=expiration_year,
            expiration_date=generated_credit_expiry,
            cvv=cvv,
            telephone=telephone,
        )

        while len(fake_data.card_number) <= 14:
            name = fake.name()
            card_number = fake.credit_card_number()
            generated_credit_expiry = fake.credit_card_expire()
            expiration_month, expiration_year = generated_credit_expiry.split("/")
            cvv = fake.credit_card_security_code()
            fake_data = CreditCardBase(
                name=name,
                card_number=card_number,
                expiration_month=expiration_month,
                expiration_year=expiration_year,
                cvv=cvv,
            )
        cc_mapping = {
            "card_number": "credit_card_number",
            "name": "name",
            "expiration_year": "credit_card_expire",
            "expiration_month": "credit_card_expire",
            "cvv": "credit_card_security_code",
        }
        if original_data:
            for field, faker_method in cc_mapping.items():
                new_cc_data = getattr(fake_data, field)
                while new_cc_data == getattr(original_data, field):
                    new_cc_data = getattr(fake, faker_method)()
                    if field in {"expiration_year", "expiration_month"}:
                        new_cc_data = (
                            new_cc_data.split("/")[0]
                            if field == "expiration_month"
                            else new_cc_data.split("/")[1]
                        )
                setattr(fake_data, field, new_cc_data)

        return fake_data

    def write_css_properties(
        self, file_path: str, element: WebElement, driver: Firefox, chrome=False
    ):
        """
        Executes JavaScript to get all of the CSS properties of a WebElement then dumps it in the specified file path location. Outputs in JSON format
        """
        css_properties = ""
        if chrome:
            with driver.context(driver.CONTEXT_CHROME):
                css_properties = driver.execute_script(
                    """
                    var s = window.getComputedStyle(arguments[0]);
                    var props = {};
                    for (var i = 0; i < s.length; i++) {
                        props[s[i]] = s.getPropertyValue(s[i]);
                    }
                    return props;
                """,
                    element,
                )

        else:
            css_properties = driver.execute_script(
                """
                    var s = window.getComputedStyle(arguments[0]);
                    var props = {};
                    for (var i = 0; i < s.length; i++) {
                        props[s[i]] = s.getPropertyValue(s[i]);
                    }
                    return props;
                """,
                element,
            )

        with open(file_path, "w") as file:
            json.dump(css_properties, file, indent=4)
        logging.info(f"CSS properties saved to {file_path}")

    def match_regex(self, pattern: str, to_match: List[str]) -> List[str]:
        """
        Given a list of logs/strings, this method will return the matches within the string that match the given regex expression.
        """
        matches = []
        for string in to_match:
            match = re.findall(pattern, string)
            if len(match) > 0:
                matches.append(match[0])

        return matches

    def normalize_phone_number(self, phone: str, default_country_code="1") -> str:
        """

        Given a phone number in some format, +1(xxx)-xxx-xxxx or something similar, it will strip the phone number
        to only the <country-code>xxxxxxxxxx format and return it.

        Regex is to remove phone number extensions, e.g 800-555-5555 x555
        Regex explanations: https://docs.python.org/3/library/re.html#regular-expression-syntax
        ...
        Attributes
        ----------
        phone : str
            The phone number to be normalized
        default_country_code: str
            By default this is '1' for Canadian and US codes.

        Returns
        -------
        str
            The normalized version of the phone number in the <country code>xxxxxxxxxx format
        """
        # sub out anything that matches this regex statement with an empty string to get rid of extensions in generated phone numbers
        phone = re.sub(r"\s*(?:x|ext)\s*\d*$", "", phone, flags=re.IGNORECASE)
        # sub out anything that is not a digit with the empty string to ensure the phone number is formatted with no spaces or special characters
        digits = re.sub(r"\D", "", phone)
        ret_val = ""

        # if the phone already contains the area code, ensure we only return the last 10 digits, otherwise a 10 length number is valid
        if len(digits) > 10:
            ret_val = digits[-10:]
        elif len(digits) == 10:
            ret_val = digits
        else:
            logging.warning("No valid phone number could be generated.")
            return ""

        # return with the country code and the normalized phone number
        return default_country_code + ret_val

    def decode_url(self, driver: Firefox):
        """Decode to base64"""
        base64_data = driver.current_url.split(",")[1]
        decoded_data = base64.b64decode(base64_data).decode("utf-8")
        json_data = json.loads(decoded_data)
        return json_data

    def assert_json_value(self, json_data, jsonpath_expr, expected_value):
        """Parse json and validate json search string with its value"""
        expr = parse(jsonpath_expr)
        match = expr.find(json_data)
        return (
            match[0].value == expected_value,
            f"Expected {expected_value}, but got {match[0].value}",
        )

    def get_domain_from_url(self, url: str) -> str:
        """
        Given a URL, it will extract the domain of the URL.

        For example, "https://www.example.com/path/to/page?query=123#fragment" will product "https://www.example.com"
        """
        parsed_url = urlparse(url)
        domain_parsed_url = parsed_url._replace(path="")
        return urlunparse(domain_parsed_url)

    def remove_all_non_numbers(self, item: str) -> str:
        return re.sub(r"[^\d-]", "", item)

    def get_all_attributes(self, driver: Firefox, item: WebElement) -> str:
        attributes = driver.execute_script(
            """
            let items = {};
            for (let attr of arguments[0].attributes) {
                items[attr.name] = attr.value;
            }
            return items;
        """,
            item,
        )

        ret_val = ""
        for attribute, value in attributes.items():
            ret_val += f"{attribute}: {value}\n"
        return ret_val

    def get_state_province_abbreviation(self, full_name: str) -> str:
        """
        Returns the abbreviation for a given state, province, or region full name.

        :param full_name: The full name of the state, province, or region.
        :return: The corresponding abbreviation or the full name itself if not in the dictionary.
        """
        return self.state_province_abbr.get(full_name, full_name)

    def get_country_local_translation(self, country_name: str) -> str:
        """
        Returns the local translation of the country name.

        :param country_name: The full name of the country in english
        :return: The corresponding translation in the local language or the english name itself if not in the dictionary.
        """
        return self.country_local_translation.get(country_name, country_name)

    def normalize_regional_phone_numbers(self, phone: str, region: str) -> str:
        """
        Normalizes a phone number by separating the country prefix and verifying the rest of the number as an integer.
        This is used for localization (l10n) regional tests.
        Parameters:
        -----------
        phone : str
            The phone number to be normalized.
        region : str
            The region (country) code to determine the correct country prefix.
        Returns:
        --------
        str
            The normalized phone number in the format <country-code><number>.
        """

        # Country code mapping for different regions
        country_codes = {
            "US": "1",
            "CA": "1",
            "FR": "33",
            "DE": "49",
        }

        # Sub out anything that matches this regex statement with an empty string to get rid of extensions in generated phone numbers
        phone = re.sub(r"\s*(?:x|ext)\s*\d*$", "", phone, flags=re.IGNORECASE)
        # Sub out anything that is not a digit with the empty string to ensure the phone number is formatted with no spaces or special characters
        digits = re.sub(r"\D", "", phone)

        # Determine country code
        country_code = country_codes.get(
            region, "1"
        )  # Default to "1" (US/CA) if region is unknown
        # handle leading zeros
        local_number = digits

        # Check if phone already contains a valid country code
        if digits.startswith(country_code):
            # Remove country code from local number
            local_number = digits[len(country_code) :]

        # Handle leading zero in local numbers (France & Germany)
        if region in ["FR", "DE"] and local_number.startswith("0"):
            # Remove the leading zero
            local_number = local_number[1:]

        # Validate local number length
        if len(local_number) < 6:  # Too short to be valid
            logging.warning(f"Invalid phone number format: {phone}")
            return ""

        # Return formatted phone number with correct country code
        return f"{country_code}{local_number}"


class BrowserActions:
    """
    Shortcut methods for things that are unsightly in Selenium-Python.

    ...

    Attributes
    ----------
    driver : selenium.webdriver.Firefox
        The instance of WebDriver under test.
    """

    def __init__(self, driver: Firefox):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout=2)

    def clear_and_fill(self, webelement: WebElement, term: str, press_enter=True):
        """
        Given a WebElement, send it the string `term` to it followed by optionally pressing ENTER.
        Default will press ENTER after sending the term to the weblement unless specified otherwise

        Parameters
        ----------
        webelement : selenium.webdriver.remote.webelement.WebElement
            The WebElement to interact with.
        term : str
            The string to send to this element.
        press_enter : bool, optional
            Whether to press Enter after sending the term (default is True).
        """
        webelement.clear()
        webelement.send_keys(term)
        if press_enter:
            webelement.send_keys(Keys.RETURN)

    def search(self, term: str, with_enter=True):
        """
        Type something into the Awesome Bar. By default, press Enter.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            url_bar = self.driver.find_element(By.ID, "urlbar-input")
            url_bar.clear()
            if with_enter:
                url_bar.send_keys(term, Keys.RETURN)
            else:
                url_bar.send_keys(term)

    def filter_elements_by_attr(
        self, elements: list[WebElement], attr: str, value: str
    ) -> list[WebElement]:
        """
        Given a list of WebElements, return the ones where attribute `attr` has value `value`.
        """
        return [el for el in elements if el.get_attribute(attr) == value]

    def pick_element_from_list_by_text(
        self, elements: list[WebElement], substr: str
    ) -> WebElement:
        """
        Given a list of WebElements, return the one where innerText matches `substr`.
        Return None if no matches. Raise RuntimeError if more than one matches.
        """
        matches = [el for el in elements if substr in el.get_attribute("innerText")]
        if len(matches) == 1:
            return matches[0]
        elif len(matches) == 0:
            return None
        else:
            raise RuntimeError("More than one element matches text.")

    def switch_to_iframe_context(self, iframe: WebElement):
        """
        Switches the context to the passed in iframe webelement.
        """
        self.driver.switch_to.frame(iframe)

    def switch_to_content_context(self):
        """
        Switches back to the normal context
        """
        self.driver.switch_to.default_content()

    def select_file_opening_option(self, option: str = "handleInternally"):
        """
        select an option when file opening window prompt is shown
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.find_element(By.ID, option).click()
            confirm_button = self.driver.find_element(By.ID, "unknownContentTypeWindow")
            sleep(2)
            confirm_button.send_keys(Keys.ENTER)

    def get_all_colors_in_element(self, selector: tuple) -> set:
        """
        Given an element selector, return all the unique colors in that element.
        """
        el = self.driver.find_element(*selector)
        u = Utilities()
        image_loc = f"{u.random_string(7)}.png"
        self.driver.save_screenshot(image_loc)

        # Get browser window size and scroll position
        scroll_position = self.driver.execute_script(
            "return { x: window.scrollX, y: window.scrollY };"
        )

        # Get device pixel ratio
        device_pixel_ratio = self.driver.execute_script(
            "return window.devicePixelRatio;"
        )

        # Get X and Y minima and maxima given view position and ratio
        link_loc = el.location
        link_size = el.size
        x_start = int((link_loc["x"] - scroll_position["x"]) * device_pixel_ratio)
        y_start = int((link_loc["y"] - scroll_position["y"]) * device_pixel_ratio)
        x_end = x_start + int(link_size["width"] * device_pixel_ratio)
        y_end = y_start + int(link_size["height"] * device_pixel_ratio)

        # Get pixel color values for every pixel in the element, return the set
        shot_image = Image.open(image_loc)
        colors = []
        logging.info(
            f"Checking colors in x = ({x_start} : {x_end}), y = ({y_start} : {y_end})"
        )
        for x in range(x_start, x_end):
            for y in range(y_start, y_end):
                colors.append(shot_image.getpixel((x, y)))
        remove(image_loc)
        return set(colors)


class PomUtils:
    """
    Shortcut methods for POM and BOM related activities.

    ...

    Attributes
    ----------
    driver : selenium.webdriver.Firefox
        The instance of WebDriver under test.
    """

    allowed_selectors_shadow_chrome_element = set([By.ID, By.CLASS_NAME, By.TAG_NAME])

    def __init__(self, driver: Firefox):
        self.driver = driver

    def get_shadow_content(
        self, element: WebElement
    ) -> list[Union[WebElement, ShadowRoot]]:
        """
        Given a WebElement, return the shadow DOM root or roots attached to it. Returns a list.
        """
        logging.info(f"Getting shadow nodes from root {element}")

        def shadow_from_script():
            shadow_children = self.driver.execute_script(
                "return arguments[0].shadowRoot.children", element
            )
            if len(shadow_children) and any(shadow_children):
                logging.info("Returning script-returned shadow elements")
                shadow_elements = [s for s in shadow_children if s is not None]
                return shadow_elements

        try:
            logging.info("Getting shadow content...")
            shadow_root = element.shadow_root
            shadow_content = [shadow_root]
            if not shadow_content:
                logging.info("Selenium shadow nav returned no elements in Shadow DOM")
                return shadow_from_script()
            return shadow_content
        except InvalidArgumentException:
            logging.info("Selenium shadow nav failed.")
            return shadow_from_script()
        except WebDriverException:
            logging.info("Cannot use Selenium shadow nav in CONTEXT_CHROME")
            return shadow_from_script()
        return []

    def css_selector_matches_element(
        self, element: Union[WebElement, ShadowRoot], selector: list
    ) -> bool:
        if isinstance(element, ShadowRoot):
            return False
        sel = f'"{selector[1]}"'
        return self.driver.execute_script(
            f"return arguments[0].matches({sel})", element
        )

    def find_shadow_chrome_element(
        self, nodes: list[WebElement], selector: list
    ) -> Union[WebElement, None]:
        logging.info("Selecting element in Chrome Context Shadow DOM...")
        if selector[0] not in self.allowed_selectors_shadow_chrome_element:
            raise ValueError(
                "Currently shadow elements in chrome can only be selected by ID, tag and class name."
            )
        for node in nodes:
            node_html = self.driver.execute_script(
                "return arguments[0].outerHTML;", node
            )
            if selector[0] == By.ID:
                tag = f'id="{selector[1]}"'
            elif selector[0] == By.CLASS_NAME:
                tag = f'class="{selector[1]}"'
            elif selector[0] == By.TAG_NAME:
                tag = selector[1]
            elif selector[0] == By.CSS_SELECTOR:
                if self.css_selector_matches_element(node, selector):
                    return node
            logging.info(f"Looking for {tag}")
            logging.info(f"Shadow element code: {node_html}")
            if tag in node_html:
                logging.info("Element found, returning...")
                return node

        return None

    def find_shadow_element(
        self,
        shadow_parent: Union[WebElement, ShadowRoot],
        selector: list,
        multiple=False,
        context="content",
    ) -> WebElement:
        """
        Given a WebElement with a shadow root attached, find a selector in the
        shadow DOM of that root.
        """
        original_timeout = self.driver.timeouts.implicit_wait
        matches = []
        logging.info(f"Requesting shadow nodes from root {shadow_parent}...")
        logging.info(f"Searching for {selector}...")
        shadow_nodes = self.get_shadow_content(shadow_parent)
        logging.info(f"Found {len(shadow_nodes)} shadow nodes...")
        logging.info(f"Looking for {selector}...")
        if context == "chrome":
            return self.find_shadow_chrome_element(shadow_nodes, selector)
        self.driver.implicitly_wait(0)
        for node in shadow_nodes:
            if self.css_selector_matches_element(node, selector):
                # If we collect shadow children via JS, and one matches the selector, we're good.
                self.driver.implicitly_wait(original_timeout)
                return node
            elements = node.find_elements(*selector)
            if elements:
                logging.info("Found a match")
                matches.extend(elements)
        self.driver.implicitly_wait(original_timeout)
        if not multiple:
            if len(matches) == 1:
                logging.info("Returning match...")
                logging.info(matches[0].get_attribute("outerHTML"))
                return matches[0]
            elif len(matches):
                logging.info("Refining matches...")
                # If we match multiple, chances are the selector is too vague
                # Except when we get multiple of the exact same thing?
                # Prefer interactable elements, then just choose one
                actables = [
                    el
                    for el in matches
                    if el.is_displayed()
                    and el.is_enabled()
                    and not el.get_attribute("hidden")
                ]
                if len(actables) == 1:
                    logging.info("Only one interactable element...")
                    return actables[0]
                elif len(actables) > 1:
                    logging.info("Multiple interactable elements...")
                    matches = actables

                first_el_classes = matches[0].get_attribute("class")
                if all(
                    [el.get_attribute("class") == first_el_classes for el in matches]
                ):
                    return matches[0]
                for el in matches:
                    logging.info("match:")
                    logging.info(el.get_attribute("outerHTML"))
                raise WebDriverException(
                    "More than one element matched within a Shadow DOM"
                )
            else:
                logging.info("No matches found.")
                return None
        else:
            if not matches:
                logging.info("No matches found.")
            return matches
