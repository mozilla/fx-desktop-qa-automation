import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888571"


def test_demo_ad_clear_tel_email(
        driver: Firefox,
        region: str,
        address_autofill: AddressFill,
        util: Utilities,
        autofill_popup: AutofillPopup
):
    """
    C2888571 - Verify clear functionality after selecting an entry from tele/email fields
    """