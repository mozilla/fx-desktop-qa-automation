from modules.page_base import BasePage


class FxaNewAccount(BasePage):
    """Page Object Model for FxA signup flow"""

    URL_TEMPLATE = "{fxa_url}"

    def sign_up_sign_in(self, email: str) -> BasePage:
        """From the entry point, enter email to sign up or sign in"""
        self.fill("login-email-input", email, press_enter=False)
        self.get_element("submit-button").click()
        return self

    def create_new_account(self, password: str, age=30) -> BasePage:
        """Fill out the password and age fields, then submit and wait for code"""
        self.fill("password-input", password, press_enter=False)
        self.fill("password-repeat-input", password, press_enter=False)
        self.fill("age-input", str(age), press_enter=False)
        self.get_element("submit-button").click()
        self.element_has_text("card-header", "Enter confirmation code")
        return self

    def confirm_new_account(self, otp: str) -> BasePage:
        """Given an OTP, confirm the account, submit, and wait for account activation"""
        self.fill("otp-input", otp, press_enter=False)
        self.get_element("submit-button").click()
        self.element_exists("connected-heading")
        return self

    def finish_account_setup(self, password: str) -> BasePage:
        """Walk through the 'Finish Account Setup' flow"""
        self.wait_for_num_tabs(2)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.fill("login-password-input", password, press_enter=False)
        self.get_element("submit-button").click()
        return self
