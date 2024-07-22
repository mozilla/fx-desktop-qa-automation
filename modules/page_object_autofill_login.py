from modules.page_object_autofill import Autofill


class LoginAutofill(Autofill):
    """
    Page Object Model for the form autofill demo page with many logins
    """

    URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/password_manager/login_and_pw_change_forms.html"

    class LoginForm:
        """
        Sub class of the Login Autofill Form where you can interact with the Login Form
        """

        def __init__(self, parent: "LoginAutofill") -> None:
            self.parent = parent
            self.username_field = None
            self.password_field = None
            self.submit_button = None

        def fill_username(self, username: str) -> None:
            if self.username_field is None:
                username_fields = self.parent.get_elements("username-field")
                self.username_field = username_fields[1]
            self.username_field.send_keys(username)

        def fill_password(self, password: str) -> None:
            if self.password_field is None:
                password_fields = self.parent.get_elements(
                    "input-field", labels=["current-password"]
                )
                self.password_field = password_fields[0]
            self.password_field.send_keys(password)

        def submit(self) -> None:
            if self.submit_button is None:
                submit_buttons = self.parent.get_elements("submit-form")
                self.submit_button = submit_buttons[0]
            self.submit_button.click()
