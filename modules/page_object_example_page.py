from selenium.webdriver.common.by import By

from modules.page_base import BasePage


class ExamplePage(BasePage):
    """
    Page Object Model for the website https://example.com/
    """

    URL_TEMPLATE = "https://example.com/"
    TITLE = "Example Domain"
    MORE_INFO_URL = "https://www.iana.org/help/example-domains"
    MORE_INFO_TITLE = "Example Domains"

    @BasePage.context_content
    def search_selected_header_via_context_menu(self):
        """Open the page, triple-click the body text, right-click it to trigger the context menu."""
        self.open()
        text = (By.TAG_NAME, "p")
        self.triple_click(text)
        self.context_click(text)
