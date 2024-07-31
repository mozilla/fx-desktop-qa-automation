import logging
from typing import Tuple

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import PanelUi
from modules.page_object import FxaHome


@pytest.fixture()
def fxa_env():
    return "stage"


@pytest.fixture()
def fxa_test_account():
    return ("dte_stage_permanent@restmail.net", "Test123???")


# Attempts to deflake this have not been entirely successful
@pytest.mark.unstable
def test_sync_existing_fxa(
    driver: Firefox,
    fxa_test_account: Tuple[str, str],
    restmail_session,
    get_otp_code,
    screenshot,
):
    """C131098: User is able to log in with existing FxAccount"""
    (username, password) = fxa_test_account
    panel_ui = PanelUi(driver)
    panel_ui.click_sync_sign_in_button()
    fxa = FxaHome(driver)
    fxa.sign_up_sign_in(username)
    fxa.fill_password(password)

    try:
        fxa.custom_wait(timeout=5).until(
            EC.presence_of_element_located(fxa.get_selector("otp-input"))
        )
        otp = get_otp_code(restmail_session)
        logging.info(f"otp code: {otp}")
        fxa.fill_otp_code(otp)
    except (NoSuchElementException, TimeoutException):
        pass
    with driver.context(driver.CONTEXT_CHROME):
        screenshot("screenshot_test_sync_existing_fxa_chrome")
    panel_ui.confirm_sync_in_progress()
