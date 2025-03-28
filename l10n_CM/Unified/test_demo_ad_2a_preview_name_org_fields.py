import logging

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888557"


def test_demo_ad_hover_name_org(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    util: Utilities,
    autofill_popup: AutofillPopup,
):
    """
    C2888557 - Verify Autofill Preview on hover over dropdown entries for name/org fields
    """
    # Create fake data and fill it in
    address_autofill.open()
    autofill_data = util.fake_autofill_data(region)
    address_autofill.save_information_basic(autofill_data)

    # Click the "Save" button
    autofill_popup.click_doorhanger_button("save")

    # Hover over each field and check data preview
    fields_to_test = ["name", "organization"]
    for field in fields_to_test:
        address_autofill.check_autofill_preview_for_field(
            field, autofill_data, autofill_popup, util
        )
