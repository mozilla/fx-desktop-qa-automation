from typing import Tuple

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import PanelUi
from modules.page_object import FxaHome


@pytest.fixture()
def test_case():
    return "131098"


@pytest.fixture()
def fxa_env():
    return "stage"


@pytest.fixture()
def fxa_test_account():
    return ("dte_stage_permanent@restmail.net", "Test123???")


def test_sync_existing_fxa(
    driver: Firefox,
    fxa_test_account: Tuple[str, str],
    restmail_session,
    get_otp_code,
    screenshot,
):
    """C131098: User is able to log in with existing FxAccount"""
    (email, password) = fxa_test_account
    panel_ui = PanelUi(driver)
    panel_ui.click_sync_sign_in_button()
    fxa = FxaHome(driver)
    fxa.sign_up_sign_in(email)
    fxa.fill_password(password)
    if fxa.is_otp_input_required():
        otp = get_otp_code(restmail_session)
        fxa.fill_otp_code(otp)
    fxa.element_visible("signed-in-status")
    status_element = fxa.get_element("signed-in-status").find_element(By.TAG_NAME, "p")
    assert "You’re signed in" in status_element.text
