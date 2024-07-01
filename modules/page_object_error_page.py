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
