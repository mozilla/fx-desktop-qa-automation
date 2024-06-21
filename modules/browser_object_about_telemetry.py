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

    def find_value_in_json(self, json_obj, target_key, target_value):
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                if key == target_key and value == target_value:
                    return True
                if self.find_value_in_json(value, target_key, target_value):
                    return True
        elif isinstance(json_obj, list):
            for item in json_obj:
                if self.find_value_in_json(item, target_key, target_value):
                    return True
        return False