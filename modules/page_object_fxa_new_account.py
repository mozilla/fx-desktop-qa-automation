from modules.page_base import BasePage

class FxaNewAccount(BasePage):
    URL_TEMPLATE = "{fxa_url}"

    def sign_up_sign_in(self, email: str) -> BasePage:
        self.fill("login-email-input", email, press_enter=False)
        self.get_element("submit-button").click()
        return self

    def create_new_account(self, password: str, age=30) -> BasePage:
        self.fill("password-input", password, press_enter=False)
        self.fill("password-repeat-input", password, press_enter=False)
        self.fill("age-input", str(age), press_enter=False)
        self.get_element("submit-button").click()
        self.element_has_text("card-header", "Enter confirmation code")
        return self

    def confirm_new_account(self, otp: str) -> BasePage:
        self.fill("otp-input", otp, press_enter=False)
        self.get_element("submit-button").click()
        self.element_exists("connected-heading")
        return self

    def finish_account_setup(self, password: str) -> BasePage:
        self.fill("login-password-input", password, press_enter=False)
        self.get_element("submit-button").click()
        return self
