import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.page_object_prefs import AboutPrefs
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888568"


def test_hover_email_and_phone_autofill_preview(
        driver: Firefox,
        region: str,
        about_prefs_privacy: AboutPrefs,
        address_autofill: AddressFill,
        autofill_popup: AutofillPopup,
        util: Utilities,
):
    """
    Verify that hovering over a saved address entry in the dropdown previews all fields
    when interacting with both the Email and Phone fields.

    """
    # Open the autofill page and fill it with fake data.
    address_autofill.open()
    autofill_data = util.fake_autofill_data(region)
    address_autofill.save_information_basic(autofill_data)

    # Click the "Save" button on the autofill popup.
    autofill_popup.click_doorhanger_button("save")

    # Click inside the Email field to trigger the autofill dropdown.
    address_autofill.double_click("form-field", labels=["email"])
    # Ensure the dropdown is visible.
    autofill_popup.ensure_autofill_dropdown_visible()
    # Hover over any saved address entry (without selecting it).
    autofill_popup.hover("select-form-option")
    # Verify that the preview displays all the fields correctly.
    address_autofill.verify_autofill_data_on_hover(autofill_data, autofill_popup, util)

    # Click inside the Phone field (using the correct label "tel") to trigger the autofill dropdown.
    address_autofill.double_click("form-field", labels=["tel"])
    # Ensure the dropdown is visible.
    autofill_popup.ensure_autofill_dropdown_visible()
    # Hover over any saved address entry (without selecting it).
    autofill_popup.hover("select-form-option")
    # Verify that the preview displays all the fields correctly.
    address_autofill.verify_autofill_data_on_hover(autofill_data, autofill_popup, util)
