from modules.page_base import BasePage


class ErrorPage(BasePage):
    """
    Page Object Model for the 'Server Not Found' error page.

    Firefox renders this page (about:neterror) as a <net-error-card> web component
    with a shadow DOM. Elements are located via the shadowParent mechanism defined
    in the JSON manifest.
    """

    def get_error_title(self):
        """Get the main title text of the error page."""
        el = self.wait.until(lambda _: self.get_element("error-title"))
        return (el.get_attribute("innerText") or "").strip()

    def get_error_short_description(self):
        """Get the hostname from the error page description.

        Targets the <strong> element inside #error-intro, which contains just the
        hostname."""
        el = self.get_element("error-short-description")
        if el:
            return (el.get_attribute("innerText") or "").strip()
        return ""

    def verify_error_header(self, expected_titles: list[str], short_site: str):
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

    def click_suggestion_and_verify_redirect(self, redirect_url: str):
        """Wait for the DNS suggestion link ("Did you mean...") to point to redirect_url,
        click it, and verify the page navigates there.
        Arguments:
            redirect_url: The expected URL after clicking the suggestion link."""

        def _suggestion_points_to_redirect(_):
            el = self.get_element("error-suggestion-link")
            if el is not None and redirect_url in (el.get_attribute("href") or ""):
                return el
            return False

        link = self.wait.until(_suggestion_points_to_redirect)
        link.click()
        self.url_contains(redirect_url)
        return self
