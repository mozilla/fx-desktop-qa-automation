import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.page_object import FxaHome, GenericPage


@pytest.fixture()
def fxa_env():
    return "stage"


@pytest.fixture()
def acct_password():
    return "Test123???"


@pytest.mark.skip(
    "Stop spamming stage with fake accounts; remove when we implement acct delete"
)
def test_sync_new_fxa(driver: Firefox, fxa_url: str, new_fxa_prep: dict, get_otp_code):
    """C131094: The user is able to create a new Firefox Account"""

    # Navigate to FxA signup flow
    panel_ui = PanelUi(driver)
    page = GenericPage(driver, url="")
    panel_ui.click_sync_sign_in_button()
    page.url_contains(fxa_url)

    # Walk through the FxA setup flow
    fxa = FxaHome(driver)
    email = new_fxa_prep.restmail.email
    fxa.sign_up_sign_in(email)
    fxa.create_new_account(new_fxa_prep.password)
    otp = get_otp_code(new_fxa_prep.restmail)
    fxa.fill_otp_code(otp)
    fxa.get_element("continue-browsing-link").click()

    # Walk through the Finish Account Setup flow and confirm sync
    fxa.driver.get(fxa_url)
    fxa.get_element("submit-button").click()
    panel_ui.manage_fxa_account()
    fxa.finish_account_setup(new_fxa_prep.password)
    panel_ui.confirm_sync_in_progress()
