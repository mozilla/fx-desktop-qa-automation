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

    def is_empty(self) -> bool:
        """Checks to see if downloads page is empty"""
        found = False
        try:
            self.element_visible("no-downloads-label")
            found = True
        finally:
            return found

    def get_downloads(self) -> list:
        """Get all download targets"""
        return self.get_elements("download-target")

    def wait_for_num_downloads(self, num: int) -> BasePage:
        """Wait for the number of downloads to equal num"""
        self.expect(lambda _: len(self.get_downloads()) == num)
        return self
