import logging
import re
from random import shuffle
from typing import Literal, Union

from faker import Faker
from faker.providers import internet, misc
from selenium.common.exceptions import (
    InvalidArgumentException,
    WebDriverException,
)
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.shadowroot import ShadowRoot
from selenium.webdriver.remote.webelement import WebElement

from modules.classes.autofill_base import AutofillAddressBase
from modules.classes.credit_card import CreditCardBase


class Utilities:
    """
    Methods that may be useful, that have nothing to do with Selenium.
    """

    def __init__(self):
        pass

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
        Given a country code, try to find the associated English locale. Returns the faker object
        and whether or not the country code was valid.

        ...
        Attributes
        ----------
        country_code : str
            The two letter country code.


        Returns
        -------
        Tuple[Faker, bool]
            A tuple where the first element is the faker object, second is a boolean indicated whether or not
            the locale is valid.
        """
        locale = f"en_{country_code.upper()}"
        try:
            faker = Faker(locale)
            faker.add_provider(internet)
            faker.add_provider(misc)
            return (faker, True)
        except AttributeError:
            faker = Faker(locale)
            faker.add_provider(internet)
            faker.add_provider(misc)
            return (faker, False)

    def generate_localized_phone_US_CA(self, fake: Faker) -> str:
        """
        Generates a phone number that is valid based on the US and CA locale.

        This means that only numbers that do not start with 1 (in the actual phone number not the area code) are considered valid.

        ...
        Attributes
        ----------
        fake : Faker
            The localized Faker object

        Returns
        -------
        str
            The raw, generated phone number
        """
        phone = ""
        while True:
            phone = self.normalize_phone_number(fake.phone_number())
            if phone[:2] != "11":
                break
        return phone

    def fake_autofill_data(self, country_code: str) -> AutofillAddressBase:
        """
        Given a country code, tries to initialize the locale of the faker and generates fake data
        then returns the new AutofillAddressBase object with the fake data.

        ...
        Attributes
        ----------
        country_code : str
            The two letter country code, defaults to CA if it is not valid.
        """
        fake, valid_code = self.create_localized_faker(country_code)
        name = fake.name()
        organization = fake.company().replace(",", "")
        street_address = fake.street_address()
        address_level_2 = fake.city()
        try:
            address_level_1 = fake.state()
        except AttributeError:
            address_level_1 = fake.administrative_unit()
        postal_code = fake.postcode()
        country = "CA" if not valid_code else country_code
        email = fake.email()
        telephone = self.generate_localized_phone_US_CA(fake)

        fake_data = AutofillAddressBase(
            name=name,
            organization=organization,
            street_address=street_address,
            address_level_2=address_level_2,
            address_level_1=address_level_1,
            postal_code=postal_code,
            country=country,
            email=email,
            telephone=telephone,
        )

        return fake_data

    def fake_credit_card_data(self) -> CreditCardBase:
        """
        Generates fake information related to the CC scenarios.


        Returns
        -------
        CreditCardBase
            The object that contains all of the fake data generated.
        """
        fake = Faker()
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

        return fake_data

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

    def clear_and_fill_no_additional_keystroke(self, webelement: WebElement, term: str):
        """
        Given a WebElement, send it the string `term` with no additional keystrokes.

        ...

        Attributes
        ----------
        webelement : selenium.webdriver.remote.webelement.WebElement
        term : str
            The string to send to this element
        """
        webelement.clear()
        webelement.send_keys(term)

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
                logging.info(shadow_elements)
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
        if type(element) == ShadowRoot:
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
                return matches[0]
            elif len(matches):
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
