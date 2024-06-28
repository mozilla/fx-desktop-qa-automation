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
