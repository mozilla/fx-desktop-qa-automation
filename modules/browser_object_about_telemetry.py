import base64
import json

from modules.page_base import BasePage


class AboutTelemetry(BasePage):
    """
    The POM for the about:telemetry page

    Attributes
    ----------
    driver: selenium.webdriver.Firefox
        WebDriver object under test
    """

    URL_TEMPLATE = "about:telemetry"

    def decode_url(self):
        """Decode to base64"""
        base64_data = self.driver.current_url.split(",")[1]
        decoded_data = base64.b64decode(base64_data).decode('utf-8')
        json_data = json.loads(decoded_data)
        return json_data
