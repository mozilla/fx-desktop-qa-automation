import pytest
from selenium.webdriver import Firefox

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
    for field in AddressFill.fields:
        # hack to pass over fields that don't show up in autofill dropdown
        if field == "address-level1" and region in ["DE", "FR"]:
            continue
        address_autofill.double_click("form-field", labels=[field])
        autofill_popup.ensure_autofill_dropdown_visible()
        autofill_popup.hover("select-form-option")
        address_autofill.verify_autofill_data_on_hover(
            address_autofill_data, autofill_popup, util
        )
