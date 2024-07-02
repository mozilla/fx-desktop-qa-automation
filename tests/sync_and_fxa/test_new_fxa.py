from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.page_object import GenericPage, FxaNewAccount


@pytest.fixture()
def fxa_env():
    return "stage"

@pytest.fixture()
def acct_password():
    return "Test123???"

def test_sync_new_fxa(driver: Firefox, fxa_url: str, new_fxa_prep: dict, get_otp_code):
    panel_ui = PanelUi(driver)
    page = GenericPage(driver, url="")
    panel_ui.open_panel_menu()
    panel_ui.click_sync_sign_in_button()
    page.url_contains(fxa_url)

    fxa = FxaNewAccount(driver)
    email = new_fxa_prep["restmail"].email
    fxa.sign_up_sign_in(email)
    fxa.create_new_account(new_fxa_prep["password"])
    otp = get_otp_code()
    fxa.confirm_new_account(otp)
    fxa.get_element("continue-browsing-link").click()

    fxa.driver.get(fxa_url)
    with driver.context(driver.CONTEXT_CHROME):
        panel_ui.get_element("sync-user-button").click()
        with open("finish_him.html", "w") as fh:
            fh.write(driver.page_source)
        panel_ui.get_element("finish-account-setup-button").click()
        sleep(20)

    with open("pass_screen.html", "w") as fh:
        fh.write(driver.page_source)
    fxa.get_element("sign-in-button").click()
    # fxa.finish_account_setup(new_fxa_prep["password"])
    # panel_ui.confirm_sync_in_progress()

