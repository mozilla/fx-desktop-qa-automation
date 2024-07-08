import re

from selenium.webdriver.remote.webelement import WebElement

from modules.page_base import BasePage


class WikiFirefoxLogo(BasePage):
    """
    Page Object Model for https://en.wikipedia.org/wiki/Firefox#/media/File:Firefox_logo,_2019.svg
    """

    URL_TEMPLATE = (
        "https://en.wikipedia.org/wiki/Firefox#/media/File:Firefox_logo,_2019.svg"
    )

    def get_image(self) -> WebElement:
        """
        Returns the WebElement associated with the image on the URL TEMPLATE
        """
        return self.get_element("firefox-logo")

    def verify_opened_image_url(self):
        self.url_contains("wikimedia")
        current_url = self.driver.current_url

        pattern = r"https://upload\.wikimedia\.org/wikipedia/commons/thumb/a/a0/Firefox_logo%2C_2019\.svg/\d+px-Firefox_logo%2C_2019\.svg\.png"
        assert re.match(
            pattern, current_url
        ), f"URL does not match the expected pattern: {current_url}"
