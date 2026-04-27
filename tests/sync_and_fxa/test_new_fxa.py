import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import PanelUi
from modules.page_object import FxaHome, GenericPage


@pytest.fixture()
def test_case():
    return "131094"


@pytest.fixture()
def fxa_env():
    return "stage"


def test_sync_new_fxa(driver: Firefox, fxa_url: str, fxa_session: dict, get_otp_code):
    """C131094: The user is able to create a new Firefox Account"""

    # Navigate to FxA signup flow
    panel_ui = PanelUi(driver)
    page = GenericPage(driver, url="")
    panel_ui.click_sync_sign_in_button()
    page.url_contains(fxa_url)

    # Walk through the FxA setup flow
    fxa = FxaHome(driver)
    email = fxa_session.restmail.email
    fxa.sign_up_sign_in(email)
    fxa.create_new_account(fxa_session.password)
    otp = get_otp_code(fxa_session.restmail)
    fxa.fill_otp_code(otp)

    # Walk through the Finish Account Setup flow and confirm sync
    panel_ui.manage_fxa_finish_sign_in()
    fxa.finish_account_setup(fxa_session.password)
    status_element = fxa.get_element("signed-in-status").find_element(By.TAG_NAME, "p")
    assert "You’re signed in" in status_element.text
