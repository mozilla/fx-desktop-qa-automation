import logging
from time import sleep

import pytest
from selenium.webdriver import ActionChains, Firefox
from selenium.webdriver.common.by import By

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.page_object_prefs import AboutPrefs
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888562"


@pytest.fixture()
def add_to_prefs_list(region: str):
    return [
        ("extensions.formautofill.creditCards.supportedCountries", region),
        ("extensions.formautofill.addresses.supported", "on"),
    ]


def test_hover_address_is_previewed(
    driver: Firefox,
    region: str,
    about_prefs_privacy: AboutPrefs,
    address_autofill: AddressFill,
    autofill_popup: AutofillPopup,
    util: Utilities,
):
    """
    C2888562: Verify that hovering over field will preview all fields
    """
    # Create fake data and fill it in
    address_autofill.open()
    address_autofill_data = util.fake_autofill_data(region)
    address_autofill.save_information_basic(address_autofill_data)

    # Click the "Save" button
    autofill_popup.click_doorhanger_button("save")

    # Hover over each field and check data preview
    # for field in AddressFill.fields:
    address_autofill.double_click("form-field", labels=["name"])
    autofill_popup.element_visible("select-form-option")
    autofill_popup.hover("select-form-option")
    with driver.context(driver.CONTEXT_CHROME):
        element = autofill_popup.get_element("address-preview-form-container")
        children = [
            x.get_attribute("innerHTML")
            for x in element.find_elements(By.TAG_NAME, "span")
            if x.get_attribute("innerHTML").strip()
        ]
        logging.warning(children)
        logging.warning(element.get_attribute("innerHTML"))
        # address_autofill.verify_autofill_data(address_autofill_data, region, util)
