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
    address_autofill.open()
    autofill_data = util.fake_autofill_data(region)
    address_autofill.save_information_basic(autofill_data)
    autofill_popup.click_doorhanger_button("save")

    # Check Email field preview.
    address_autofill.check_autofill_preview_for_field("email", autofill_data, autofill_popup, util)
    # Check Phone field preview (using the correct label "tel").
    address_autofill.check_autofill_preview_for_field("tel", autofill_data, autofill_popup, util)