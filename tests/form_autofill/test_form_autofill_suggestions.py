import platform

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object_autofill import CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122401"


indices = range(2)


@pytest.mark.xfail(platform.system() == "Linux", reason="Autofill Linux instability")
@pytest.mark.parametrize("index", indices)
def test_form_autofill_suggestions(driver: Firefox, index: str):
    """
    C122401, checks that the corresponding autofill suggestion autofills the fields correctly
    """
    # instantiate objects
    util = Utilities()

    credit_card_fill_obj = CreditCardFill(driver).open()
    autofill_popup_obj = AutofillPopup(driver)

    # create fake data, two profiles
    sample_data = [
        credit_card_fill_obj.fake_and_fill(util, autofill_popup_obj) for _ in range(2)
    ]

    # press the corresponding option (according to the parameter)
    credit_card_fill_obj.click_on("form-field", labels=["cc-name"])

    # verify information based, verify based on second object if we are verifying first option (this is the newer option) and
    # vice versa
    check_index = 1 - index
    credit_card_fill_obj.verify_four_fields(
        autofill_popup_obj, sample_data[check_index]
    )
