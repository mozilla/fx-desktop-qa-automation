from modules.page_base import BasePage


class AboutDownloads(BasePage):
    """
    The POM for the about:downloads page

    Attributes
    ----------
    driver: selenium.webdriver.Firefox
        WebDriver object under test
    """

    URL_TEMPLATE = "about:downloads"

    def is_empty(self):
        """Checks to see if downloads page is empty"""
        found = False
        try:
            self.element_visible("no-downloads-label")
            found = True
        finally:
            return found
