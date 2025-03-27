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
    address_autofill.fill_and_save(util, autofill_popup)

    # Open dropdown and select first option and clear autofill form
    address_autofill.select_autofill_option(autofill_popup, "name")
    address_autofill.click_on("form-field", labels=["name"])
    # Verify that the form autofill suggestions are displayed.
    autofill_popup.verify_element_displayed("select-form-option")
