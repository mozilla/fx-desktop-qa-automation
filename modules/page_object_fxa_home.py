import json

from modules.classes.fxa_session import FxaSession
from modules.page_base import BasePage


class FxaHome(BasePage):
    """Page Object Model for FxA pages"""

    URL_TEMPLATE = "{fxa_url}"

    def sign_up_sign_in(self, email: str) -> BasePage:
        """From the entry point, enter email to sign up or sign in"""
        self.fill("login-email-input", email, press_enter=False)
        self.get_element("submit-button").click()
        return self

    def fill_password(self, password: str) -> BasePage:
        self.set_content_context()
        self.fill("login-password-input", password, press_enter=False)
        self.get_element("submit-button").click()
        return self

    def is_otp_input_required(self) -> bool:
        return len(self.get_elements("otp-input")) > 0

    def create_new_account(self, password: str, age=30) -> BasePage:
        """Fill out the password and age fields, then submit and wait for code"""
        self.fill("signup-password-input", password, press_enter=False)
        self.fill("signup-password-repeat-input", password, press_enter=False)
        self.element_clickable("submit-button")
        self.get_element("submit-button").click()
        self.element_has_text("card-header", "Enter confirmation code")
        return self

    def fill_otp_code(self, otp: str) -> BasePage:
        """Given an OTP, confirm the account, submit, and wait for account activation"""
        self.fill("otp-input", otp, press_enter=False)
        self.get_element("submit-button").click()
        self.title_contains("Set up Firefox sync")
        self.title_contains("Mozilla accounts")
        return self

    def fill_passwordless_code(self, otp: str) -> BasePage:
        """Enter the emailed one-time code on the passwordless code screen and submit"""
        self.fill("passwordless-code-input", otp, press_enter=False)
        self.click_on("submit-button")
        return self

    def finish_account_setup(self, password: str) -> BasePage:
        """Walk through the 'Finish Account Setup' flow"""
        self.wait_for_num_tabs(2)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.fill("login-password-input", password, press_enter=False)
        self.get_element("submit-button").click()
        self.element_visible("signed-in-status")
        return self

    def set_localstorage_item(self, key: str, value: str) -> BasePage:
        """Set a localStorage item for the current page's origin"""
        self.driver.execute_script(
            "window.localStorage.setItem(arguments[0], arguments[1]);", key, value
        )
        return self

    def inject_session(self, fxa_session: FxaSession) -> BasePage:
        """
        Store a verified account session in the current FxA page and reload it,
        so FxA offers the cached account instead of the sign-in form.

        Must be called on the FxA tab Firefox opened, so the page keeps the
        OAuth parameters of the flow Firefox is waiting on.

        Parameters
        ----------
        fxa_session : FxaSession
            A session from the create_fxa fixture.
        """
        assert fxa_session.session is not None, "Call create_account() first"
        # Wait for the FxA app itself; localStorage is not available on the
        # about:blank the new tab starts on.
        self.element_visible("login-email-input")
        uid = fxa_session.session.uid
        account = {
            "email": fxa_session.restmail.email,
            "uid": uid,
            "sessionToken": fxa_session.session.token,
            "verified": True,
            "sessionVerified": True,
        }
        self.set_localstorage_item("__fxa_storage.accounts", json.dumps({uid: account}))
        self.set_localstorage_item("__fxa_storage.currentAccountUid", json.dumps(uid))
        self.driver.refresh()
        self.element_visible("cached-signin-submit")
        return self

    def continue_with_cached_account(self) -> BasePage:
        """Continue as the cached account on FxA's returning-user screen"""
        self.click_on("cached-signin-submit")
        return self

    @BasePage.context_chrome
    def install_waf_bypass_header(self, token: str, hosts: list[str]) -> BasePage:
        """
        Register a chrome-level HTTP observer that adds the fxa-ci WAF-bypass
        header to requests for the given FxA hosts, so browser navigation (not
        just PyFxA's API calls) can reach WAF-protected FxA hosts.

        The observer sees every request Firefox sends but only changes those to
        `hosts`, and stays active until cleanup_waf_bypass_header is called.

        Mirrors the nsIHttpChannel interceptor in fxa's own
        packages/functional-tests/lib/fixtures/pairing.ts.

        Parameters
        ----------
        token : str
            The WAF-bypass token (CI_WAF_TOKEN).
        hosts : list[str]
            Hostnames that should receive the header.
        """
        self.driver.execute_script(
            """
            // Runs in the browser's privileged (chrome) context, so it sees every
            // HTTP request Firefox makes, not just those from the current page.
            const [token, hosts] = arguments;

            // Remove an observer left by an earlier call, so only one is ever active.
            if (window.__fxaWafBypassCleanup) {
              window.__fxaWafBypassCleanup();
            }

            // Called for each outgoing HTTP request, just before it is sent. Only
            // requests to the FxA hosts get the fxa-ci header; all others are left
            // untouched. The final `false` replaces any existing value rather than
            // appending to it.
            function wafObserver(subject) {
              const channel = subject.QueryInterface(Ci.nsIHttpChannel);
              if (hosts.includes(channel.URI.host)) {
                channel.setRequestHeader("fxa-ci", token, false);
              }
            }

            // "http-on-modify-request" is the notification Firefox sends at that point.
            Services.obs.addObserver(wafObserver, "http-on-modify-request");

            // Store an unregister function on this browser window, so
            // cleanup_waf_bypass_header (or a repeat call) can remove the observer.
            window.__fxaWafBypassCleanup = () => {
              Services.obs.removeObserver(wafObserver, "http-on-modify-request");
              delete window.__fxaWafBypassCleanup;
            };
            """,
            token,
            hosts,
        )
        return self

    @BasePage.context_chrome
    def cleanup_waf_bypass_header(self) -> BasePage:
        """Remove the WAF-bypass observer installed by install_waf_bypass_header"""
        self.driver.execute_script(
            """
            if (window.__fxaWafBypassCleanup) {
              window.__fxaWafBypassCleanup();
            }
            """
        )
        return self
