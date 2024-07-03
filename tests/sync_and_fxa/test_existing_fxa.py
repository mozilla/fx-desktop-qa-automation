from typing import Tuple

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.page_object import FxaHome, GenericPage


@pytest.fixture()
def fxa_env():
    return "stage"


@pytest.fixture()
def fxa_test_account():
    return ("dte_stage_permanent@restmail.net", "Test123???")


def test_sync_existing_fxa(driver: Firefox, fxa_test_account: Tuple[str, str]):
    (username, password) = fxa_test_account
    panel_ui = PanelUi(driver)
    panel_ui.click_sync_sign_in_button()
    fxa = FxaHome(driver)
    fxa.sign_up_sign_in(username)
    fxa.fill_password(password)
    panel_ui.confirm_sync_in_progress()
