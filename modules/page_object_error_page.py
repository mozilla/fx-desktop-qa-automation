import json
from urllib.parse import parse_qs, urlparse

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from modules.page_base import BasePage


class ErrorPage(BasePage):
    """
    Page Object Model for the 'Server Not Found' error page.

    Firefox 138+ renders this page as a <net-error-card> web component with a shadow DOM.
    Elements are located via the shadowParent mechanism defined in the JSON manifest.
    """

    def get_error_title(self) -> str:
        """Get the main title text of the error page."""
        el = WebDriverWait(self.driver, 10).until(
            lambda _: self.get_element("error-title")
        )
        return (el.get_attribute("innerText") or "").strip()

    def get_error_short_description(self) -> str:
        """Get the short description text from the error page.

        Reads the hostname from the data-l10n-args attribute on the description
        element, falling back to innerText and then the 'd' URL parameter."""
        el = self.get_element("error-short-description")
        if el:
            l10n_args = el.get_attribute("data-l10n-args")
            if l10n_args:
                return json.loads(l10n_args).get("hostname", "")
            text = (el.get_attribute("innerText") or "").strip()
            if text:
                return text
        params = parse_qs(urlparse(self.driver.current_url).query)
        return params.get("d", [""])[0]

    def get_error_learn_more_link(self) -> WebElement:
        """Get the 'Learn more' link element."""
        return self.get_element("error-learn-more-link")

    def verify_error_header(self, expected_titles: list[str], short_site: str) -> None:
        """Verify the main title and that the site name appears in the error page description.
        Arguments:
            expected_titles: The valid header title for the error page.
            short_site: The short version of the site URL (eg. "example" from "http://example")."""
        title = self.get_error_title()
        desc = self.get_error_short_description()
        assert title in expected_titles, f"Title was: {title!r}"
        assert short_site in desc, (
            f"Expected {short_site!r} in description, got: {desc!r}"
        )

    def click_learn_more_and_verify_redirect(self, redirect_url: str) -> "BasePage":
        """Wait for the 'Learn more' link to point to redirect_url, click it, and verify the redirect.
        Arguments:
            redirect_url: The expected URL after clicking the learn more link."""

        def _get_learn_more(driver):
            el = self.get_element("error-learn-more-link")
            return el is not None and redirect_url in (el.get_attribute("href") or "")

        WebDriverWait(self.driver, 10).until(_get_learn_more)
        initial_window_count = len(self.driver.window_handles)
        self.get_element("error-learn-more-link").click()
        self.wait_for_num_tabs(initial_window_count + 1)
        self.switch_to_new_tab()
        self.url_contains(redirect_url)
        return self
