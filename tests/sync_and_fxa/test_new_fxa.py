import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.page_object import FxaNewAccount, GenericPage


@pytest.fixture()
def fxa_env():
    return "stage"


@pytest.fixture()
def acct_password():
    return "Test123???"


def test_sync_new_fxa(driver: Firefox, fxa_url: str, new_fxa_prep: dict, get_otp_code):
    """C131094: The user is able to create a new Firefox Account"""

    # Navigate to FxA signup flow
    panel_ui = PanelUi(driver)
    page = GenericPage(driver, url="")
    panel_ui.click_sync_sign_in_button()
    page.url_contains(fxa_url)

    # Walk through the FxA setup flow
    fxa = FxaNewAccount(driver)
    email = new_fxa_prep["restmail"].email
    fxa.sign_up_sign_in(email)
    fxa.create_new_account(new_fxa_prep["password"])
    otp = get_otp_code()
    fxa.confirm_new_account(otp)
    fxa.get_element("continue-browsing-link").click()

    # Walk through the Finish Account Setup flow and confirm sync
    fxa.driver.get(fxa_url)
    fxa.get_element("sign-in-button").click()
    panel_ui.manage_fxa_account()
    fxa.finish_account_setup(new_fxa_prep["password"])
    panel_ui.confirm_sync_in_progress()