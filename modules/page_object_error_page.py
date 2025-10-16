from selenium.webdriver.remote.webelement import WebElement

from modules.page_base import BasePage


class ErrorPage(BasePage):
    """
    Page Object Model for the 'Server Not Found' error page.
    """

    def get_error_title(self) -> str:
        return self.get_element("error-title").get_attribute("innerText")

    def get_error_short_description(self) -> str:
        return self.get_element("error-short-description").get_attribute("innerText")

    def get_error_long_description_items(self) -> list[WebElement]:
        return self.get_elements("error-long-description-items")

    def get_try_again_button(self) -> WebElement:
        return self.get_element("try-again-button")

    def get_error_suggestion_link(self) -> WebElement:
        return self.get_element("error-suggestion-link")

    def verify_error_header(self, expected_titles: list[str], short_site: str) -> None:
        """Verify the main title and short description on the error page.
        Arguments:
            expected_titles: The list of valid titles accepted for the error page.
            short_site: The short version of the site URL (e.g., "example" from "http://example").
        """
        assert self.get_error_title() in expected_titles
        assert (
            f"We can’t connect to the server at {short_site}"
            in self.get_error_short_description()
        )

    def verify_error_bullets(
        self,
        expected_texts: list[str],
        possible_permission_messages: list[str],
    ) -> None:
        """Verify bullet items under the long description section.
        Arguments:
            expected_texts: The list of exact text strings expected for the first two bullet items.
            possible_permission_messages: The list of valid permission-related messages accepted for the third bullet item.
        """
        items = self.get_error_long_description_items()
        assert len(items) >= 3
        # First two must match exactly
        for i in range(2):
            assert items[i].text == expected_texts[i]
        # Third must match one of the permission messages
        assert items[2].text in possible_permission_messages

    def click_suggestion_and_verify_redirect(self, redirect_url: str) -> None:
        """Click the suggestion link and verify it redirects correctly.
        Arguments:
            redirect_url: The expected URL after clicking the suggestion link.
        """
        self.get_error_suggestion_link().click()
        self.url_contains(redirect_url)
