import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122574"


def test_clear_form(
    driver: Firefox,
    address_autofill: AddressFill,
    autofill_popup: AutofillPopup,
    util: Utilities,
    region: str,
):
    """
    C122574, test clear autofill form

    Arguments:
        autofill_popup: AutofillPopup instance
        util: Utilities instance
        region: country code in use
    """
    # open address page
    address_autofill.open()

    # create fake data, fill it in and press submit and save on the doorhanger
    autofill_sample_data = util.fake_autofill_data(region)
    address_autofill.save_information_basic(autofill_sample_data)
    autofill_popup.click_doorhanger_button("save")

    # Open dropdown and select first option and clear autofill form
    address_autofill.triple_click("form-field", labels=["name"])
    autofill_popup.click_autofill_form_option()
    address_autofill.click_on("form-field", labels=["name"])
    # Verify that the form autofill suggestions are displayed.
    autofill_popup.verify_element_displayed("select-form-option")
