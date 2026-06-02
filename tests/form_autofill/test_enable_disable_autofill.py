import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object import AboutPrefs, AddressFill


@pytest.fixture()
def prefs_category():
    return "passwordsAutofill"


@pytest.fixture()
def test_case():
    return "122347"


def test_enable_disable_autofill(
    driver: Firefox,
    about_prefs: AboutPrefs,
    address_autofill: AddressFill,
    autofill_popup: AutofillPopup,
    region: str,
):
    """
    C122347, tests that after filling autofill and disabling it in settings that
    the autofill popups do not appear.

    Arguments:
        about_prefs: AboutPrefs instance (privacy category)
        autofill_popup: AutofillPopup instance
    """
    address_autofill.open()

    # scroll to first form field
    address_autofill.scroll_to_form_field()

    # Scroll to form field
    address_autofill.scroll_to_form_field()

    # create fake data, fill it in and press submit and save on the doorhanger
    address_autofill.fill_and_save()

    about_prefs.open()
    about_prefs.get_element("save-and-fill-addresses").click()

    address_autofill.open()

    # scroll to first form field
    address_autofill.scroll_to_form_field()

    # verifying the popup panel does not appear
    address_autofill.double_click("form-field", labels=["name"])
    autofill_popup.ensure_autofill_dropdown_not_visible()
