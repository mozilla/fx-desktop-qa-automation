from modules.page_base import BasePage


class ExamplePage(BasePage):
    """
    Page Object Model for the website https://example.com/
    """

    URL_TEMPLATE = "https://example.com/"
    TITLE = "Example Domain"
    MORE_INFO_URL = "https://www.iana.org/help/example-domains"
    MORE_INFO_TITLE = "Example Domains"
