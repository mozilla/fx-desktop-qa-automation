from modules.page_base import BasePage


class FxaNewAccount(BasePage):
    URL_TEMPLATE = ""

    def sign_up_sign_in(email: str) -> BasePage:
        self.get_element("login-email-input").clear().send_keys(email)
        self.get_element("submit-button").click()
        return self

    def create_new_account(password: str, age=30) -> BasePage:
        self.get_element("password-input").clear().send_keys(password)
        self.get_element("password-repeat-input").clear().send_keys(password)
        self.get_element("age-input").clear().send_keys(str(age))
        self.get_element("submit-button").click()
        return self

    def confirm_new_account(otp: str) -> BasePage:
        self.get_element("otp-input").clear().send_keys(otp)
        self.get_element("submit-button").click()
        return self
